/*
 * Copyright (C) 2018, 2019 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 * The universal solving function, works with any solver.
 *
 * The functions contain the essential core of a minimization solver.
 */

#include "adjust_solveFunc.h"

// STL
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <limits>
#include <memory>
#include <stdio.h>
#include <string>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDagPath.h>
#include <maya/MDGContext.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnPluginData.h>
#include <maya/MGlobal.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MProfiler.h>
#include <maya/MStreamUtils.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20180000
#include <maya/MDGContextGuard.h>
#endif

// MM Scene Graph
#include <mmscenegraph/mmscenegraph.h>

// MM Solver
#include "mmSolver/core/mmdata.h"
#include "mmSolver/core/mmmath.h"
#include "mmSolver/lens/lens_model.h"
#include "mmSolver/node/MMLensData.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"
#include "adjust_base.h"
#include "adjust_data.h"


namespace mmsg = mmscenegraph;

// NOTE: There is a very strange bug in Maya. After setting a number
// of plug values using a DG Context, when quering plug values at the
// same times, the values do not evaluate correctly. To 'trick' Maya
// into triggering an eval the next time a plug is queried we query
// the matrix of a marker node. It doesn't matter which marker node,
// however it does matter that it's a marker node, if the eval is
// performed with a bundle node the error continues to happen.
#define FORCE_TRIGGER_EVAL 1


// Pre-processor-level on/off switch for re-use of the Marker
// positions. This is an optimisation to avoid re-evaluating the
// Marker values from the Maya DG in the solving evaluation loop.
#define USE_MARKER_POSITION_CACHE 1


// Calculate the smoothness/stiffness error values without needing a
// 'variance' value.
#define CALC_SMOOTHNESS_STIFFNESS_WITHOUT_VARIANCE 0


#if MAYA_API_VERSION < 201700
int getStringArrayIndexOfValue(MStringArray &array, MString &value) {
    int index = -1;
    for (unsigned int i=0; i<array.length(); ++i) {
        if (array[i] == value) {
            index = i;
            break;
        }
    }
    return index;
}
#endif


/*
 * Generate a 'dgdirty' MEL command listing all nodes that may be
 * changed by our solve function.
 */
MString generateDirtyCommand(int numberOfMarkerErrors, SolverData *ud) {
    MString dgDirtyCmd = "dgdirty ";
    MStringArray dgDirtyNodeNames;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];

        MarkerPtr marker = ud->markerList[markerPair.first];
        MString markerName = marker->getNodeName();
#if MAYA_API_VERSION >= 201700
        const int markerName_idx = dgDirtyNodeNames.indexOf(markerName);
#else
        const int markerName_idx = getStringArrayIndexOfValue(dgDirtyNodeNames, markerName);
#endif
        if (markerName_idx == -1) {
            dgDirtyCmd += " \"" + markerName + "\" ";
            dgDirtyNodeNames.append(markerName);
        }

        CameraPtr camera = marker->getCamera();
        MString cameraTransformName = camera->getTransformNodeName();
        MString cameraShapeName = camera->getShapeNodeName();
#if MAYA_API_VERSION >= 201700
        const int cameraTransformName_idx = dgDirtyNodeNames.indexOf(cameraTransformName);
#else
        const int cameraTransformName_idx = getStringArrayIndexOfValue(dgDirtyNodeNames, cameraTransformName);
#endif
        if (cameraTransformName_idx == -1) {
            dgDirtyCmd += " \"" + cameraTransformName + "\" ";
            dgDirtyNodeNames.append(cameraTransformName);
        }
#if MAYA_API_VERSION >= 201700
        const int cameraShapeName_idx = dgDirtyNodeNames.indexOf(cameraShapeName);
#else
        const int cameraShapeName_idx =  getStringArrayIndexOfValue(dgDirtyNodeNames, cameraShapeName);
#endif
        if (cameraShapeName_idx == -1) {
            dgDirtyCmd += " \"" + cameraShapeName + "\" ";
            dgDirtyNodeNames.append(cameraShapeName);
        }

        BundlePtr bundle = marker->getBundle();
        MString bundleName = bundle->getNodeName();
#if MAYA_API_VERSION >= 201700
        const int bundleName_idx = dgDirtyNodeNames.indexOf(bundleName);
#else
        const int bundleName_idx = getStringArrayIndexOfValue(dgDirtyNodeNames, bundleName);
#endif
        if (bundleName_idx == -1) {
            dgDirtyCmd += " \"" + bundleName + "\" ";
            dgDirtyNodeNames.append(bundleName);
        }
    }
    dgDirtyCmd += ";";
    return dgDirtyCmd;
}


// Given a specific parameter, calculate the expected 'delta' value of
// the parameter.
double calculateParameterDelta(double value,
                               double delta,
                               double sign,
                               AttrPtr attr) {
    MStatus status = MS::kSuccess;
    double xmin = attr->getMinimumValue();
    double xmax = attr->getMaximumValue();

    // If the value +/- delta would cause the attribute to go
    // out of box-constraints, then we should only use one
    // value, or go in the other direction.
    if ((value + delta) > xmax) {
        sign = -1;
    }
    if ((value - delta) < xmin) {
        sign = 1;
    }
    return delta * sign;
}


MStatus
calculateMarkerLensModelList(
    const MarkerPtrList &markerList,
    const MTimeArray &frameList,
    std::vector<std::unique_ptr<LensModel>> &out_markerLensModelList
) {
    MStatus status = MS::kSuccess;

    auto num_frames = frameList.length();
    auto num_markers = markerList.size();
    out_markerLensModelList.resize(num_markers * num_frames);

    uint32_t added_lens_count = 0;
    for (uint32_t i = 0; i < num_markers; ++i) {
        MarkerPtr marker = markerList[i];
        CameraPtr camera = marker->getCamera();

        auto camera_shape_mobj = camera->getShapeObject();
        MFnDependencyNode mfn_depend_node(camera_shape_mobj, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get output lens data.
        const MString attr_name = "outLens";
        const bool want_networked_plug = true;
        MPlug plug = mfn_depend_node.findPlug(attr_name, want_networked_plug, &status);
        if (status != MS::kSuccess) {
            // The camera may not have an 'outLens' attribute and may
            // not have a lens node connected to it.
            status = MS::kSuccess;
            continue;
        }

        for (uint32_t j = 0; j < num_frames; j++) {
            MTime frame = frameList[j];

            MDGContext ctx(frame);
#if MAYA_API_VERSION >= 20180000
            MDGContextGuard ctxGuard(ctx);
            MObject data_object = plug.asMObject(&status);
#else
            MObject data_object = plug.asMObject(ctx, &status);
#endif
            CHECK_MSTATUS(status);
            if (status != MS::kSuccess) {
                return status;
            }
            if (data_object.isNull()) {
                continue;
            }

            MFnPluginData pluginDataFn(data_object);
            const mmsolver::MMLensData* outputLensData =
                (const mmsolver::MMLensData*) pluginDataFn.constData(&status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            if (outputLensData != nullptr) {
                auto nodeLensModel = outputLensData->getValue();
                if (nodeLensModel != nullptr) {
                    auto nodeLensModelClone = nodeLensModel->clone();
                    nodeLensModelClone->initModel();

                    // This indexing structure ensures lenses on the
                    // same frame are tightly packed, which increases
                    // cache locality.
                    auto index = (i * num_frames) + j;
                    out_markerLensModelList[index] = std::move(nodeLensModelClone);
                    ++added_lens_count;
                }
            }
        }
    }

    if (added_lens_count == 0) {
        // Effectively disables lens distortion for the solve.
        out_markerLensModelList.clear();
    }

    return status;
}


// Set Parameter values
MStatus
setParameters_mayaDag(
        const int numberOfParameters,
        const double *parameters,
        SolverData *ud) {
    MStatus status = MS::kSuccess;

    MTime currentFrame = MAnimControl::currentTime();
    for (int i = 0; i < numberOfParameters; ++i) {
        const IndexPair attrPair = ud->paramToAttrList[i];
        AttrPtr attr = ud->attrList[attrPair.first];

        const double offset = attr->getOffsetValue();
        const double scale = attr->getScaleValue();
        const double xmin = attr->getMinimumValue();
        const double xmax = attr->getMaximumValue();
        const double solver_value = parameters[i];
        const double real_value = parameterBoundFromInternalToExternal(
            solver_value,
            xmin, xmax,
            offset, scale);

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            frame = ud->frameList[attrPair.second];
        }

        status = attr->setValue(real_value, frame, *ud->dgmod, *ud->curveChange);
        if (status != MS::kSuccess) {
            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            MMSOLVER_ERR(
                "setParameters (Maya DAG) was given an invalid value to set:"
                << " frame=" << frame
                << " attr name=" << attr_name_char
                << " solver value=" << solver_value
                << " bound value=" << real_value
                << " offset=" << offset
                << " scale=" << scale
                << " min=" << xmin
                << " max=" << xmax);

            break;
        }
    }

    // Commit changed data into Maya
    ud->dgmod->doIt();

    // Invalidate the Camera Matrix cache.
    //
    // In future we might be able to auto-detect if the camera
    // will change based on the current solve and not invalidate
    // the cache but for now we cannot take the risk of an
    // incorrect solve; we clear the cache.
    for (int i = 0; i < (int) ud->cameraList.size(); ++i) {
        ud->cameraList[i]->clearAttrValueCache();
    }

    return status;
}


MStatus
setParameters_mmSceneGraph(
        const int numberOfParameters,
        const double *parameters,
        SolverData *ud) {
    MStatus status = MS::kSuccess;
    MTime currentFrame = MAnimControl::currentTime();

    for (int i = 0; i < numberOfParameters; ++i) {
        const IndexPair attrPair = ud->paramToAttrList[i];
        AttrPtr attr = ud->attrList[attrPair.first];

        const double offset = attr->getOffsetValue();
        const double scale = attr->getScaleValue();
        const double xmin = attr->getMinimumValue();
        const double xmax = attr->getMaximumValue();
        // The solver value is used inside the solver to compute the
        // result, but is not the true value that will be set on the
        // attribute at the end of the solve.
        const double solver_value = parameters[i];
        const double real_value = parameterBoundFromInternalToExternal(
            solver_value,
            xmin, xmax,
            offset, scale);

        const auto object_type = attr->getObjectType();
        if (object_type != ObjectType::kLens) {
            mmsg::FrameValue frame = 0;
            if (attrPair.second != -1) {
                frame = ud->mmsgFrameList[attrPair.second];
            }

            mmsg::AttrId attrId = ud->mmsgAttrIdList[attrPair.first];
            auto ok = ud->mmsgAttrDataBlock.set_attr_value(attrId, frame, real_value);
            if (!ok) {
                status = MS::kFailure;

                MString attr_name = attr->getName();
                auto attr_name_char = attr_name.asChar();

                MMSOLVER_ERR(
                    "setParameters (MMSG) was given an invalid value to set:"
                    << " attr name=" << attr_name_char
                    << " solver value=" << solver_value
                    << " bound value=" << real_value
                    << " offset=" << offset
                    << " scale=" << scale
                    << " min=" << xmin
                    << " max=" << xmax);
                break;
            }
        } else {
            // Set the Maya DAG Lens node attributes.
            MTime frame = currentFrame;
            if (attrPair.second != -1) {
                frame = ud->frameList[attrPair.second];
            }

            status = attr->setValue(real_value, frame, *ud->dgmod, *ud->curveChange);
            if (status != MS::kSuccess) {
                MString attr_name = attr->getName();
                auto attr_name_char = attr_name.asChar();

                MMSOLVER_ERR(
                    "setParameters (MMSG) was given an invalid value to set:"
                    << " frame=" << frame
                    << " attr name=" << attr_name_char
                    << " solver value=" << solver_value
                    << " bound value=" << real_value
                    << " offset=" << offset
                    << " scale=" << scale
                    << " min=" << xmin
                    << " max=" << xmax);

                break;
            }
        }
    }

    return status;
}

// Set Parameter values
MStatus
setParameters(
        const int numberOfParameters,
        const double *parameters,
        SolverData *ud) {
    MStatus status = MS::kSuccess;

    const SceneGraphMode sceneGraphMode = ud->solverOptions->sceneGraphMode;
    if (sceneGraphMode == SceneGraphMode::kMayaDag) {
        status = setParameters_mayaDag(
            numberOfParameters,
            parameters,
            ud);

#if MMSOLVER_LENS_DISTORTION == 1 && MMSOLVER_LENS_DISTORTION_MAYA_DAG == 1
        if (ud->markerLensModelList.size() > 0) {
            status = calculateMarkerLensModelList(
                ud->markerList,
                ud->frameList,
                ud->markerLensModelList
            );
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
#endif
    } else if (sceneGraphMode == SceneGraphMode::kMMSceneGraph) {
        status = setParameters_mmSceneGraph(
            numberOfParameters,
            parameters,
            ud);

#if MMSOLVER_LENS_DISTORTION == 1 && MMSOLVER_LENS_DISTORTION_MM_SCENE_GRAPH == 1
        if (ud->markerLensModelList.size() > 0) {
            status = calculateMarkerLensModelList(
                ud->markerList,
                ud->frameList,
                ud->markerLensModelList
            );
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
#endif
    } else {
        MMSOLVER_ERR(
            "setParameters failed, invalid SceneGraphMode: "
            << static_cast<int>(sceneGraphMode));
        status = MS::kFailure;
    }

    // Save a copy of the parameters - to be used for determining the
    // the difference between the previous and next parameters to be
    // set inside Maya.
    for (int j = 0; j < numberOfParameters; ++j) {
        ud->previousParamList[j] = parameters[j];
    }

    return status;
}


inline
double gaussian(double x, double mean, double sigma) {
    return std::exp(
            -(std::pow((x - mean), 2.0) / (2.0 * (std::pow(sigma, 2.0))))
    );
}


/*
 * Compare the previous and new parameters to see which parameters
 * have changed. This allows us to only update and measure the changed
 * markers and attributes - speeding up the evaluation.
 */
void determineMarkersToBeEvaluated(int numberOfParameters,
                                   int numberOfMarkers,
                                   double delta,
                                   std::vector<double> previousParamList,
                                   const double *parameters,
                                   std::vector<std::vector<bool>> errorToParamList,
                                   std::vector<bool> &evalMeasurements) {
    std::vector<int> evalCount(numberOfMarkers, 0);

    // Get all parameters that have changed.
    double approxDelta = std::fabs(delta) * 0.5;
    bool noneChanged = true;
    std::vector<bool> paramChangedList(numberOfParameters, false);
    for (int i = 0; i < numberOfParameters; ++i) {
        bool changed = !number::isApproxEqual<double>(
            parameters[i], previousParamList[i], approxDelta);
        paramChangedList[i] = changed;
        if (changed) {
            noneChanged = false;
        }
    }

    // Find if a marker does not need to be updated at all.
    for (int i = 0; i < numberOfParameters; ++i) {
        bool changed = paramChangedList[i];
        if (noneChanged == true) {
            changed = true;
        }
        for (int j = 0; j < numberOfMarkers; ++j) {
            if (changed && errorToParamList[j][i]) {
                evalCount[j] = evalCount[j] + 1;
            }
        }
    }

    // Convert evalCount to list of bools
    evalMeasurements.resize((unsigned long) numberOfMarkers, false);
    for (size_t i = 0; i < evalCount.size(); ++i) {
        evalMeasurements[i] = static_cast<bool>(evalCount[i] > 0);
    }
    return;
}

inline
double distance_2d(
    const double ax, const double ay,
    const double bx, const double by
) {
    double dx = ax - bx;
    double dy = ay - by;
    return std::sqrt((dx * dx) + (dy * dy));
}

void measureErrors_mayaDag(
        const int numberOfErrors,
        const int numberOfMarkerErrors,
        const int numberOfAttrStiffnessErrors,
        const int numberOfAttrSmoothnessErrors,
        const std::vector<bool> &frameIndexEnable,
        const std::vector<bool> &errorMeasurements,
        double *errors,
        SolverData *ud,
        double &error_avg,
        double &error_max,
        double &error_min,
        MStatus &status) {
    UNUSED(numberOfErrors);

    // Trigger an DG Evaluation at a different time, to help Maya
    // evaluate at the correct frame.
    const int timeEvalMode = ud->solverOptions->timeEvalMode;

#if FORCE_TRIGGER_EVAL == 1
    {
        MPoint pos;
        int i = 0;
        IndexPair markerPair = ud->errorToMarkerList[i];
        MarkerPtr marker = ud->markerList[markerPair.first];
        MTime frame = ud->frameList[markerPair.second];
        status = marker->getPos(pos, frame + 1, TIME_EVAL_MODE_DG_CONTEXT);
        CHECK_MSTATUS(status);
    }
#endif

    auto num_frames = ud->frameList.length();
    auto num_marker_lens_models = ud->markerLensModelList.size();

    // Compute Marker Errors
    MMatrix cameraWorldProjectionMatrix;
    MPoint mkr_mpos;
    MPoint bnd_mpos;
    int numberOfErrorsMeasured = 0;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];
        int markerIndex = markerPair.first;
        int frameIndex = markerPair.second;

        bool skipFrame = frameIndexEnable[frameIndex] == false;
        bool skipMarker = errorMeasurements[i] == false;
        if (skipFrame) {
            // Skip evaluation of this marker error. The 'errors' data
            // is expected to be unchanged from the last evaluation.
            continue;
        }
        if (skipMarker) {
            // Skip calculation of the error if errorMeasurements says
            // not to calculate it. The errorMeasurements is expected
            // to be pre-computed and 'know' something this function does
            // not about the greater structure of the solving problem.
            continue;
        }

        MarkerPtr marker = ud->markerList[markerIndex];
        MTime frame = ud->frameList[frameIndex];

        CameraPtr camera = marker->getCamera();
        status = camera->getWorldProjMatrix(cameraWorldProjectionMatrix, frame,
                                            timeEvalMode);
        CHECK_MSTATUS(status);

        MVector cam_dir;
        MPoint cam_pos;
        camera->getWorldPosition(cam_pos, frame, timeEvalMode);
        camera->getForwardDirection(cam_dir, frame, timeEvalMode);

        BundlePtr bnd = marker->getBundle();

        double mkr_x = 0.0;
        double mkr_y = 0.0;
#if USE_MARKER_POSITION_CACHE == 1
        mkr_mpos = ud->markerPosList[i];
        mkr_x = mkr_mpos.x;
        mkr_y = mkr_mpos.y;
#else
        status = marker->getPosXY(mkr_x, mkr_y, frame, timeEvalMode);
        CHECK_MSTATUS(status);
#endif
        // Scale marker Y.
        {
            double filmBackWidth = camera->getFilmbackWidthValue(frame, timeEvalMode);
            double filmBackHeight = camera->getFilmbackHeightValue(frame, timeEvalMode);
            int32_t renderWidth = camera->getRenderWidthValue();
            int32_t renderHeight = camera->getRenderHeightValue();
            double filmBackAspect = filmBackWidth / filmBackHeight;
            double renderAspect =
                static_cast<double>(renderWidth) / static_cast<double>(renderHeight);
            double aspect = renderAspect / filmBackAspect;
            mkr_y *= aspect;
        }

#if MMSOLVER_LENS_DISTORTION == 1 && MMSOLVER_LENS_DISTORTION_MAYA_DAG == 1
        auto markerLensModelIndex = (frameIndex * num_frames) + markerIndex;
        if (markerLensModelIndex < num_marker_lens_models
            && ud->markerLensModelList[markerLensModelIndex] != nullptr) {
            double out_x = mkr_x;
            double out_y = mkr_y;
            ud->markerLensModelList[markerLensModelIndex]->applyModel(
                mkr_x,
                mkr_y,
                out_x,
                out_y
            );

            // Applying the lens distortion model to large input
            // values, creates NaN undistorted points.
            if (std::isfinite(out_x)) {
                mkr_x = out_x;
            }
            if (std::isfinite(out_y)) {
                mkr_y = out_y;
            }
        }
#endif

        double mkr_weight = ud->markerWeightList[i];
        assert(mkr_weight > 0.0);  // 'sqrt' will be NaN if the weight is less than 0.0.
        mkr_weight = std::sqrt(mkr_weight);

        // Re-project Bundle into screen-space.
        MVector bnd_dir;
        status = bnd->getPos(bnd_mpos, frame, timeEvalMode);
        CHECK_MSTATUS(status);
        MPoint bnd_mpos_tmp(bnd_mpos);
        bnd_dir = bnd_mpos_tmp - cam_pos;
        bnd_dir.normalize();
        bnd_mpos = bnd_mpos * cameraWorldProjectionMatrix;
        bnd_mpos.cartesianize();
        // Convert to -0.5 to 0.5 range for 2D coordinates inside the
        // film back.
        bnd_mpos[0] *= 0.5;
        bnd_mpos[1] *= 0.5;

        // Is the bundle behind the camera?
        bool behind_camera = false;
        double behind_camera_error_factor = 1.0;
        double cam_dot_bnd = cam_dir * bnd_dir;
        // MMSOLVER_WRN("Camera DOT Bundle: " << cam_dot_bnd);
        if (cam_dot_bnd < 0.0) {
            behind_camera = true;
            behind_camera_error_factor = 1e+6;
        }

        // According to the Ceres solver 'circle_fit.cc'
        // example, using the 'sqrt' distance error function is a
        // bad idea as it will introduce non-linearities, we are
        // better off using something like 'x*x - y*y'. It would
        // be best to test this detail.
        const double dx = std::fabs(mkr_x - bnd_mpos.x) * ud->imageWidth;
        const double dy = std::fabs(mkr_y - bnd_mpos.y) * ud->imageWidth;

        auto errorIndex_x = i * ERRORS_PER_MARKER;
        auto errorIndex_y = errorIndex_x + 1;
        errors[errorIndex_x] = dx * mkr_weight * behind_camera_error_factor;
        errors[errorIndex_y] = dy * mkr_weight * behind_camera_error_factor;

        // 'ud->errorList' is the deviation shown to the user, it
        // should not have any loss functions or scaling applied to it.
        ud->errorList[errorIndex_x] = dx * behind_camera_error_factor;
        ud->errorList[errorIndex_y] = dy * behind_camera_error_factor;

        const double d = distance_2d(mkr_x, mkr_y, bnd_mpos[0], bnd_mpos[1]) * ud->imageWidth;
        ud->errorDistanceList[i] = d;
        error_avg += d;
        if (d > error_max) { error_max = d; }
        if (d < error_min) { error_min = d; }
        ++numberOfErrorsMeasured;
    }
    if (numberOfErrorsMeasured == 0) {
        error_max = 0.0;
        error_min = 0.0;
        error_avg = 0.0;
        MMSOLVER_ERR("No Marker measurements were taken.");
    } else {
        error_avg *= 1.0 / numberOfErrorsMeasured;
    }

    // Compute the stiffness values for the the attributes of the 'error' array.
    // Stiffness is an error weighting back to the previous value.
    double attrValue = 0.0;
    double stiffValue = 0.0;
    double stiffWeight = 0.0;
    double stiffVariance = 1.0;
    const int stiffIndexOffset = 0;
    for (int i = 0; i < numberOfAttrStiffnessErrors; ++i) {
        int indexIntoErrorArray = numberOfMarkerErrors + stiffIndexOffset + i;
        StiffAttrsPtr stiffAttrs = ud->stiffAttrsList[i];
        int attrIndex = stiffAttrs->attrIndex;
        AttrPtr stiffWeightAttr = stiffAttrs->weightAttr;
        AttrPtr stiffVarianceAttr = stiffAttrs->varianceAttr;
        AttrPtr stiffValueAttr = stiffAttrs->valueAttr;
        AttrPtr attr = ud->attrList[attrIndex];

        // Query the current value of the value, and calculate
        //  the difference between the stiffness value.
        stiffWeightAttr->getValue(stiffWeight, timeEvalMode);
        stiffVarianceAttr->getValue(stiffVariance, timeEvalMode);
        stiffValueAttr->getValue(stiffValue, timeEvalMode);
        attr->getValue(attrValue, timeEvalMode);

#if CALC_SMOOTHNESS_STIFFNESS_WITHOUT_VARIANCE == 1
        auto straight_line = mmdata::Point2D(1.0, 0.0);
        auto new_line = mmdata::Point2D(1.0, stiffValue - attrValue);
        auto straight_line_norm = mmmath::normalize(straight_line);
        auto new_line_norm = mmmath::normalize(new_line);
        double error = 1.0 / std::fabs(mmmath::dot(straight_line_norm, new_line_norm));
#else
        double error = ((1.0 / gaussian(attrValue, stiffValue, stiffVariance)) - 1.0);
#endif

        ud->errorList[indexIntoErrorArray] = error * stiffWeight;
        errors[indexIntoErrorArray] = error * stiffWeight;
    }

    // Compute the smoothness values for the the attributes of the 'error' array.
    // Smoothness is an error weighting to the predicted next value that is smooth.
    double smoothValue = 0.0;
    double smoothWeight = 0.0;
    double smoothVariance = 1.0;
    const int smoothIndexOffset = numberOfAttrStiffnessErrors;
    for (int i = 0; i < numberOfAttrSmoothnessErrors; ++i) {
        int indexIntoErrorArray = numberOfMarkerErrors + smoothIndexOffset + i;
        SmoothAttrsPtr smoothAttrs = ud->smoothAttrsList[i];
        int attrIndex = smoothAttrs->attrIndex;
        AttrPtr smoothWeightAttr = smoothAttrs->weightAttr;
        AttrPtr smoothVarianceAttr = smoothAttrs->varianceAttr;
        AttrPtr smoothValueAttr = smoothAttrs->valueAttr;
        AttrPtr attr = ud->attrList[attrIndex];

        // Query the current value of the value, and calculate
        //  the difference between the smoothness value.
        smoothWeightAttr->getValue(smoothWeight, timeEvalMode);
        smoothVarianceAttr->getValue(smoothVariance, timeEvalMode);
        smoothValueAttr->getValue(smoothValue, timeEvalMode);
        attr->getValue(attrValue, timeEvalMode);

#if CALC_SMOOTHNESS_STIFFNESS_WITHOUT_VARIANCE == 1
        auto straight_line = mmdata::Point2D(1.0, 0.0);
        auto new_line = mmdata::Point2D(1.0, smoothValue - attrValue);
        auto straight_line_norm = mmmath::normalize(straight_line);
        auto new_line_norm = mmmath::normalize(new_line);
        double error = 1.0 / std::fabs(mmmath::dot(straight_line_norm, new_line_norm));
#else
        double error = ((1.0 / gaussian(attrValue, smoothValue, smoothVariance)) - 1.0);
#endif

        ud->errorList[indexIntoErrorArray] = error * smoothWeight;
        errors[indexIntoErrorArray] = error * smoothWeight;
    }

    return;
}

void measureErrors_mmSceneGraph(
        const int numberOfErrors,
        const int numberOfMarkerErrors,
        const int numberOfAttrStiffnessErrors,
        const int numberOfAttrSmoothnessErrors,
        const std::vector<bool> &frameIndexEnable,
        const std::vector<bool> &errorMeasurements,
        double *errors,
        SolverData *ud,
        double &error_avg,
        double &error_max,
        double &error_min,
        MStatus &status) {
    UNUSED(numberOfErrors);
    UNUSED(numberOfAttrStiffnessErrors);
    UNUSED(numberOfAttrSmoothnessErrors);
    UNUSED(status);

    // Evaluate Scene.
    ud->mmsgFlatScene.evaluate(
        ud->mmsgAttrDataBlock,
        ud->mmsgFrameList);

    auto num_points = ud->mmsgFlatScene.num_points();
    auto num_markers = ud->mmsgFlatScene.num_markers();
    auto num_frames = ud->mmsgFrameList.size();
    auto num_marker_lens_models = ud->markerLensModelList.size();
    UNUSED(num_points);
    UNUSED(num_markers);
    assert(num_points == num_markers);

    auto out_point_list = ud->mmsgFlatScene.points();
    auto out_marker_list = ud->mmsgFlatScene.markers();
    assert(out_marker_list.size() == out_point_list.size());

    // Count Marker Errors
    int numberOfErrorsMeasured = 0;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];
        int markerIndex = markerPair.first;
        int frameIndex = markerPair.second;

        bool skipFrame = frameIndexEnable[frameIndex] == false;
        bool skipMarker = errorMeasurements[i] == false;
        if (skipFrame) {
            // Skip evaluation of this marker error. The 'errors' data
            // is expected to be unchanged from the last evaluation.
            continue;
        }
        if (skipMarker) {
            // Skip calculation of the error if errorMeasurements says
            // not to calculate it. The errorMeasurements is expected
            // to be pre-computed and 'know' something this function does
            // not about the greater structure of the solving problem.
            continue;
        }

        // Use pre-computed marker weight
        double mkr_weight = ud->markerWeightList[i];
        assert(mkr_weight > 0.0);  // 'sqrt' will be NaN if the weight is less than 0.0.
        mkr_weight = std::sqrt(mkr_weight);

        // TODO: Calculate 'behind_camera_error_factor', the same as
        // the Maya DAG function.
        double behind_camera_error_factor = 1.0;

        auto mkrIndex_x = ((markerIndex * num_frames * 2) + (frameIndex * 2));
        auto mkrIndex_y = mkrIndex_x + 1;
        auto mkr_x = out_marker_list[mkrIndex_x];
        auto mkr_y = out_marker_list[mkrIndex_y];
        auto point_x = out_point_list[mkrIndex_x];
        auto point_y = out_point_list[mkrIndex_y];

#if MMSOLVER_LENS_DISTORTION == 1 && MMSOLVER_LENS_DISTORTION_MM_SCENE_GRAPH == 1
        auto markerLensModelIndex = (frameIndex * num_frames) + markerIndex;
        if (markerLensModelIndex < num_marker_lens_models
            && ud->markerLensModelList[markerLensModelIndex] != nullptr) {
            double out_x = mkr_x;
            double out_y = mkr_y;
            ud->markerLensModelList[markerLensModelIndex]->applyModel(
                mkr_x,
                mkr_y,
                out_x,
                out_y
            );

            // Applying the lens distortion model to large input
            // values, creates NaN undistorted points.
            if (std::isfinite(out_x)) {
                mkr_x = out_x;
            }
            if (std::isfinite(out_y)) {
                mkr_y = out_y;
            }
        }
#endif

        auto dx = std::fabs(mkr_x - point_x);
        auto dy = std::fabs(mkr_y - point_y);
        auto dx_pixels = dx * ud->imageWidth;
        auto dy_pixels = dy * ud->imageWidth;

        auto errorIndex_x = i * ERRORS_PER_MARKER;
        auto errorIndex_y = errorIndex_x + 1;
        errors[errorIndex_x] = dx_pixels * mkr_weight * behind_camera_error_factor;
        errors[errorIndex_y] = dy_pixels * mkr_weight * behind_camera_error_factor;

        // 'ud->errorList' is the deviation shown to the user, it
        // should not have any loss functions or scaling applied to it.
        ud->errorList[errorIndex_x] = dx_pixels * behind_camera_error_factor;
        ud->errorList[errorIndex_y] = dy_pixels * behind_camera_error_factor;

        const double d = std::sqrt((dx * dx) + (dy * dy)) * ud->imageWidth;
        ud->errorDistanceList[i] = d;
        error_avg += d;
        if (d > error_max) { error_max = d; }
        if (d < error_min) { error_min = d; }
        ++numberOfErrorsMeasured;
    }
    if (numberOfErrorsMeasured == 0) {
        error_max = 0.0;
        error_min = 0.0;
        error_avg = 0.0;
        MMSOLVER_ERR("No Marker measurements were taken.");
    } else {
        error_avg *= 1.0 / numberOfErrorsMeasured;
    }

    // TODO: Support stiffness and smoothness.

    return;
}

void measureErrors(
        const int numberOfErrors,
        const int numberOfMarkerErrors,
        const int numberOfAttrStiffnessErrors,
        const int numberOfAttrSmoothnessErrors,
        const std::vector<bool> &frameIndexEnable,
        const std::vector<bool> &errorMeasurements,
        double *errors,
        SolverData *ud,
        double &error_avg,
        double &error_max,
        double &error_min,
        MStatus &status) {
    error_avg = 0.0;
    error_max = -0.0;
    error_min = std::numeric_limits<double>::max();

    assert(ud->errorToMarkerList.size() > 0);
    assert(ud->frameList.length() > 0);

    const SceneGraphMode sceneGraphMode = ud->solverOptions->sceneGraphMode;
    if (sceneGraphMode == SceneGraphMode::kMayaDag) {
        measureErrors_mayaDag(
            numberOfErrors,
            numberOfMarkerErrors,
            numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors,
            frameIndexEnable,
            errorMeasurements,
            errors,
            ud,
            error_avg,
            error_max,
            error_min,
            status);
    } else if (sceneGraphMode == SceneGraphMode::kMMSceneGraph) {
        measureErrors_mmSceneGraph(
            numberOfErrors,
            numberOfMarkerErrors,
            numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors,
            frameIndexEnable,
            errorMeasurements,
            errors,
            ud,
            error_avg,
            error_max,
            error_min,
            status);
    }

    // Changes the errors to be scaled by the loss function.
    // This will reduce the affect outliers have on the solve.
    if (ud->solverOptions->solverSupportsRobustLoss) {
        // TODO: Scale the jacobian by the loss function too?
        applyLossFunctionToErrors(numberOfErrors, errors,
                                  ud->solverOptions->robustLossType,
                                  ud->solverOptions->robustLossScale);
    }
    assert(error_max >= error_min);
    assert(error_min <= error_max);
    return;
}


// Add another 'normal function' evaluation to the count.
void incrementNormalIteration(SolverData *ud) {
    ++ud->funcEvalNum;
    ++ud->iterNum;
    MStreamUtils::stdErrorStream() << "Iteration ";
    MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw(4)
                                   << ud->iterNum;
    MStreamUtils::stdErrorStream() << " | Eval ";
    MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw(4)
                                   << ud->funcEvalNum;
    return;
}


// Add another 'jacobian function' evaluation to the count.
void incrementJacobianIteration(SolverData *ud) {
    ++ud->funcEvalNum;
    ++ud->jacIterNum;
    if (ud->verbose) {
        MStreamUtils::stdErrorStream() << "Jacobian  ";
        MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw (4)
                                       << ud->jacIterNum;
        MStreamUtils::stdErrorStream() << " | Eval ";
        MStreamUtils::stdErrorStream() << std::right << std::setfill ('0') << std::setw (4)
                                       << ud->funcEvalNum;
        if (ud->doCalcJacobian) {
            MStreamUtils::stdErrorStream() << "\n";
        }
    }
    return;
}


// Function run by cminpack algorithm to test the input parameters, p,
// and compute the output errors, x.
int solveFunc(const int numberOfParameters,
              const int numberOfErrors,
              const double *parameters,
              double *errors,
              double *jacobian,
              void *userData) {
    SolverData *ud = static_cast<SolverData *>(userData);
    ud->timer.funcBenchTimer.start();
    ud->timer.funcBenchTicks.start();
    if (!ud->doCalcJacobian) {
        ud->computation->setProgress(ud->iterNum);
    }

    int numberOfMarkerErrors = ud->numberOfMarkerErrors;
    int numberOfAttrStiffnessErrors = ud->numberOfAttrStiffnessErrors;
    int numberOfAttrSmoothnessErrors = ud->numberOfAttrSmoothnessErrors;
    int numberOfMarkers = numberOfMarkerErrors / ERRORS_PER_MARKER;
    assert(ud->errorToParamList.size() == static_cast<size_t>(numberOfMarkers));

    if (ud->isNormalCall) {
        incrementNormalIteration(ud);
    } else if (ud->isJacobianCall && !ud->doCalcJacobian) {
        incrementJacobianIteration(ud);
    }

    if (ud->isPrintCall) {
        // insert print statements here when nprint is positive.
        //
        // if the nprint parameter to 'lmdif' or 'lmder' is positive,
        // the function is called every nprint iterations with iflag=0,
        // so that the function may perform special operations, such as
        // printing residuals.
        return SOLVE_FUNC_SUCCESS;
    }

    if (ud->computation->isInterruptRequested()) {
        MMSOLVER_WRN("User wants to cancel the evaluation!");
        ud->userInterrupted = true;
        return SOLVE_FUNC_FAILURE;
    }

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope iterScope(profileCategory,
                              MProfiler::kColorC_L1,
                              "iteration");
#endif

    bool interactive = ud->mayaSessionState == MGlobal::MMayaState::kInteractive;
    if (interactive) {
        MString dgDirtyCmd = generateDirtyCommand(numberOfMarkerErrors, ud);
        MGlobal::executeCommand(dgDirtyCmd);
    }

    // Calculate residual errors, or jacobian matrix?
    double error_avg = 0;
    double error_max = 0;
    double error_min = 0;
    if (ud->doCalcJacobian == false) {
        // A normal evaluation of the errors and parameters.
        std::vector<bool> evalMeasurements(numberOfMarkers, true);
        std::vector<bool> frameIndexEnable(ud->frameList.length(), 1);

        // Set Parameters
        MStatus status;
        {
            ud->timer.paramBenchTimer.start();
            ud->timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
            MProfilingScope setParamScope(profileCategory,
                                          MProfiler::kColorA_L2,
                                          "set parameters");
#endif
            status = setParameters(
                    numberOfParameters,
                    parameters,
                    ud);
            ud->timer.paramBenchTimer.stop();
            ud->timer.paramBenchTicks.stop();
        }

        // Measure Errors
        {
            ud->timer.errorBenchTimer.start();
            ud->timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
            MProfilingScope setParamScope(profileCategory,
                                          MProfiler::kColorA_L1,
                                          "measure errors");
#endif
            measureErrors(numberOfErrors,
                          numberOfMarkerErrors,
                          numberOfAttrStiffnessErrors,
                          numberOfAttrSmoothnessErrors,
                          frameIndexEnable,
                          evalMeasurements,
                          errors,
                          ud,
                          error_avg, error_max, error_min,
                          status);
            ud->timer.errorBenchTimer.stop();
            ud->timer.errorBenchTicks.stop();
        }
    } else {
        // Calculate Jacobian Matrix
        MStatus status;
        assert(ud->solverOptions->solverType == SOLVER_TYPE_CMINPACK_LMDER);
        int autoDiffType = ud->solverOptions->autoDiffType;

        // Get longest dimension for jacobian matrix
        int ldfjac = numberOfErrors;
        if (ldfjac < numberOfParameters) {
            ldfjac = numberOfParameters;
        }

        int progressMin = ud->computation->progressMin();
        int progressMax = ud->computation->progressMax();
        ud->computation->setProgress(progressMin);

        std::vector<bool> evalMeasurements(numberOfMarkers, false);
        determineMarkersToBeEvaluated(
                numberOfParameters,
                numberOfMarkers,
                ud->solverOptions->delta,
                ud->previousParamList,
                parameters,
                ud->errorToParamList,
                evalMeasurements);

        // Calculate the jacobian matrix.
        std::vector<double> paramListA(numberOfParameters, 0);
        std::vector<double> errorListA(numberOfErrors, 0);
        for (int i = 0; i < numberOfParameters; ++i) {
            double ratio = (double) i / (double) numberOfParameters;
            int progressNum = progressMin + static_cast<int>(ratio * progressMax);
            ud->computation->setProgress(progressNum);

            if (ud->computation->isInterruptRequested()) {
                MMSOLVER_WRN("User wants to cancel the evaluation!");
                ud->userInterrupted = true;
                return SOLVE_FUNC_FAILURE;
            }

            // Create a copy of the parameters and errors.
            for (int j = 0; j < numberOfParameters; ++j) {
                paramListA[j] = parameters[j];
            }
            for (int j = 0; j < numberOfErrors; ++j) {
                errorListA[j] = errors[j];
            }

            // Calculate the relative delta for each parameter.
            double delta = ud->solverOptions->delta;
            assert(delta > 0.0);

            // 'analytically' calculate the deviation of markers as
            //  will be affected by the new calculated delta value.
            //  This will give us a jacobian matrix, without needing
            //  to set attribute values and re-evaluate them in Maya's
            //  DG.
            IndexPair attrPair = ud->paramToAttrList[i];
            AttrPtr attr = ud->attrList[attrPair.first];
            // TODO: Get the camera that is best for the attribute,
            //  not just index 0.
            MarkerPtr mkr = ud->markerList[0];
            CameraPtr cam = mkr->getCamera();

            double value = parameters[i];
            double deltaA = calculateParameterDelta(
                    value, delta, 1, attr);

            std::vector<bool> frameIndexEnabled = ud->paramFrameList[i];

            incrementJacobianIteration(ud);
            paramListA[i] = paramListA[i] + deltaA;
            {
                ud->timer.paramBenchTimer.start();
                ud->timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
                MProfilingScope setParamScope(profileCategory,
                                              MProfiler::kColorA_L2,
                                              "set parameters");
#endif
                status = setParameters(
                        numberOfParameters,
                        &paramListA[0],
                        ud);
                ud->timer.paramBenchTimer.stop();
                ud->timer.paramBenchTicks.stop();
            }

            double error_avg_tmp = 0;
            double error_max_tmp = 0;
            double error_min_tmp = 0;
            {
                ud->timer.errorBenchTimer.start();
                ud->timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
                MProfilingScope setParamScope(profileCategory,
                                              MProfiler::kColorA_L1,
                                              "measure errors");
#endif
                // Based on only the changed attribute value only
                // measure the markers that can modify the attribute -
                // we do this using 'frameIndexEnabled' and
                // 'evalMeasurements'.
                measureErrors(numberOfErrors,
                              numberOfMarkerErrors,
                              numberOfAttrStiffnessErrors,
                              numberOfAttrSmoothnessErrors,
                              frameIndexEnabled,
                              evalMeasurements,
                              &errorListA[0],
                              ud,
                              error_avg_tmp,
                              error_max_tmp,
                              error_min_tmp,
                              status);
                ud->timer.errorBenchTimer.stop();
                ud->timer.errorBenchTicks.stop();
            }

            if (autoDiffType == AUTO_DIFF_TYPE_FORWARD) {
                assert(ud->solverOptions->solverSupportsAutoDiffForward);
                // Set the Jacobian matrix using the previously
                // calculated errors (original and A).
                double inv_delta = 1.0 / deltaA;
                for (size_t j = 0; j < errorListA.size(); ++j) {
                    size_t num = (i * ldfjac) + j;
                    double x = (errorListA[j] - errors[j]) * inv_delta;
                    ud->jacobianList[num] = x;
                    jacobian[num] = x;
                }

            } else if (autoDiffType == AUTO_DIFF_TYPE_CENTRAL) {
                assert(ud->solverOptions->solverSupportsAutoDiffCentral);
                // Create another copy of parameters and errors.
                std::vector<double> paramListB(numberOfParameters, 0);
                for (int j = 0; j < numberOfParameters; ++j) {
                    paramListB[j] = parameters[j];
                }
                std::vector<double> errorListB(numberOfErrors, 0);

                // Get the new delta, from the oposite direction. If
                // we don't calculate a different delta value, we
                // something has gone wrong and a second evaluation is
                // not needed.
                double deltaB = calculateParameterDelta(
                        value, delta, -1, attr);
                if (deltaA == deltaB) {
                    // Set the Jacobian matrix using the previously
                    // calculated errors (original and A).
                    double inv_delta = 1.0 / deltaA;
                    for (size_t j = 0; j < errorListA.size(); ++j) {
                        size_t num = (i * ldfjac) + j;
                        double x = (errorListA[j] - errors[j]) * inv_delta;
                        ud->jacobianList[num] = x;
                        jacobian[num] = x;
                    }
                } else {

                    incrementJacobianIteration(ud);
                    paramListB[i] = paramListB[i] + deltaB;
                    {
                        ud->timer.paramBenchTimer.start();
                        ud->timer.paramBenchTicks.start();
#ifdef MAYA_PROFILE
                        MProfilingScope setParamScope(profileCategory,
                                                      MProfiler::kColorA_L2,
                                                      "set parameters");
#endif
                        status = setParameters(
                                numberOfParameters,
                                &paramListB[0],
                                ud);
                        ud->timer.paramBenchTimer.stop();
                        ud->timer.paramBenchTicks.stop();
                    }

                    error_avg_tmp = 0;
                    error_max_tmp = 0;
                    error_min_tmp = 0;
                    {
                        ud->timer.errorBenchTimer.start();
                        ud->timer.errorBenchTicks.start();
#ifdef MAYA_PROFILE
                        MProfilingScope setParamScope(profileCategory,
                                                      MProfiler::kColorA_L1,
                                                      "measure errors");
#endif
                        measureErrors(numberOfErrors,
                                      numberOfMarkerErrors,
                                      numberOfAttrStiffnessErrors,
                                      numberOfAttrSmoothnessErrors,
                                      frameIndexEnabled,
                                      evalMeasurements,
                                      &errorListB[0],
                                      ud,
                                      error_avg_tmp,
                                      error_max_tmp,
                                      error_min_tmp,
                                      status);
                        ud->timer.errorBenchTimer.stop();
                        ud->timer.errorBenchTicks.stop();
                    }

                    // Set the Jacobian matrix using the previously
                    // calculated errors (A and B).
                    assert(errorListA.size() == errorListB.size());
                    double inv_delta = 0.5 / (std::fabs(deltaA) + std::fabs(deltaB));
                    for (size_t j = 0; j < errorListA.size(); ++j) {
                        size_t num = (i * ldfjac) + j;
                        double x = (errorListA[j] - errorListB[j]) * inv_delta;
                        ud->jacobianList[num] = x;
                        jacobian[num] = x;
                    }
                }
            }
        }
    }
    ud->timer.funcBenchTimer.stop();
    ud->timer.funcBenchTicks.stop();

    if (ud->isNormalCall) {
        char formatBuffer[128];
        sprintf(
            formatBuffer,
            " | error avg %8.4f   min %8.4f   max %8.4f",
            error_avg,
            error_min,
            error_max);
        MStreamUtils::stdErrorStream() << std::string(formatBuffer) << "\n";
    } else {
        if (ud->verbose) {
            if (!ud->doCalcJacobian) {
                std::cerr << "\n";
            }
        }
    }
    return SOLVE_FUNC_SUCCESS;
}


// Clean up #define
#undef FORCE_TRIGGER_EVAL
