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
 * Measure the deviation/error distances between Markers and Bundles.
 */

#include "adjust_solveFunc.h"

// STL
#include <stdio.h>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <limits>
#include <memory>
#include <string>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDGContext.h>
#include <maya/MDagPath.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnPluginData.h>
#include <maya/MGlobal.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MProfiler.h>
#include <maya/MSelectionList.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20180000
#include <maya/MDGContextGuard.h>
#endif

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Scene Graph
#include <mmscenegraph/mmscenegraph.h>

// MM Core
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

// MM Solver
#include "adjust_base.h"
#include "adjust_data.h"
#include "adjust_relationships.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_frame_utils.h"
#include "mmSolver/mayahelper/maya_lens_model_utils.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsg = mmscenegraph;

namespace mmsolver {

// NOTE: There is a very strange bug in Maya. After setting a number
// of plug values using a DG Context, when quering plug values at the
// same times, the values do not evaluate correctly. To 'trick' Maya
// into triggering an eval the next time a plug is queried we query
// the matrix of a marker node. It doesn't matter which marker node,
// however it does matter that it's a marker node, if the eval is
// performed with a bundle node the error continues to happen.
//
// 2023-02-06 (YYYY-MM-DD): Disabling this toggle. It doesn't seem to
// make any difference in real-world tests.
#define FORCE_TRIGGER_EVAL 0

// Pre-processor-level on/off switch for re-use of the Marker
// positions. This is an optimisation to avoid re-evaluating the
// Marker values from the Maya DG in the solving evaluation loop.
#define USE_MARKER_POSITION_CACHE 1

// Calculate the smoothness/stiffness error values without needing a
// 'variance' value.
#define CALC_SMOOTHNESS_STIFFNESS_WITHOUT_VARIANCE 0

inline double gaussian(double x, double mean, double sigma) {
    return std::exp(
        -(std::pow((x - mean), 2.0) / (2.0 * (std::pow(sigma, 2.0)))));
}

inline double distance_2d(const double ax, const double ay, const double bx,
                          const double by) {
    double dx = ax - bx;
    double dy = ay - by;
    return std::sqrt((dx * dx) + (dy * dy));
}

void measureErrors_mayaDag(const int numberOfErrors,
                           const int numberOfMarkerErrors,
                           const int numberOfAttrStiffnessErrors,
                           const int numberOfAttrSmoothnessErrors,
                           const std::vector<bool> &frameIndexEnable,
                           const std::vector<bool> &errorMeasurements,
                           const double imageWidth, double *errors,
                           SolverData *ud, double &error_avg, double &error_max,
                           double &error_min, MStatus &status) {
    MMSOLVER_CORE_UNUSED(numberOfErrors);

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
        MMSOLVER_CHECK_MSTATUS(status);
    }
#endif

    auto num_frames = ud->frameList.size();
    auto num_marker_lens_models = ud->lensModelList.size();

    // Compute Marker Errors
    const auto ui_unit = MTime::uiUnit();
    MMatrix cameraWorldProjectionMatrix;
    MPoint mkr_mpos;
    MPoint bnd_mpos;
    int numberOfErrorsMeasured = 0;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = ud->errorToMarkerList[i];
        const MarkerIndex markerIndex = markerPair.first;
        const FrameIndex frameIndex = markerPair.second;

        const bool skipFrame = frameIndexEnable[frameIndex] == false;
        const bool skipMarker = errorMeasurements[i] == false;
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

        if (frameIndex != -1) {
            const Count32 enabledAttrs =
                countEnabledAttrsForMarkerToAttrToFrameRelationship(
                    markerIndex, frameIndex, ud->markerToAttrToFrameMatrix);
            if (enabledAttrs == 0) {
                continue;
            }
        }

        MarkerPtr marker = ud->markerList.get_marker(markerIndex);
        const FrameNumber frameNumber = ud->frameList.get_frame(frameIndex);
        const MTime frame = convert_to_time(frameNumber, ui_unit);

        CameraPtr camera = marker->getCamera();
        status = camera->getWorldProjMatrix(cameraWorldProjectionMatrix, frame,
                                            timeEvalMode);
        MMSOLVER_CHECK_MSTATUS(status);

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
        bool applyOverscan = true;
        status =
            marker->getPosXY(mkr_x, mkr_y, frame, timeEvalMode, applyOverscan);
        MMSOLVER_CHECK_MSTATUS(status);
#endif

        const int16_t filmFit = camera->getFilmFitValue();
        const double filmBackWidth =
            camera->getFilmbackWidthValue(frame, timeEvalMode);
        const double filmBackHeight =
            camera->getFilmbackHeightValue(frame, timeEvalMode);
        const int32_t renderWidth = camera->getRenderWidthValue();
        const int32_t renderHeight = camera->getRenderHeightValue();

        const double filmBackAspect = filmBackWidth / filmBackHeight;
        const double renderAspect = static_cast<double>(renderWidth) /
                                    static_cast<double>(renderHeight);

        // The Marker position must be scaled slightly based on the
        // Camera's FilmFit attribute, because the camera projection
        // matrix already has the same scale factors embedded in the
        // matrix.
        //
        // This is only needed for the 'Maya DAG' mode, because the
        // 'MM SceneGraph' (Rust) code already accounts for this
        // change.
        applyFilmFitCorrectionScaleBackward(filmFit, filmBackAspect,
                                            renderAspect, mkr_x, mkr_y);

        double mkr_weight = ud->markerWeightList[i];
        MMSOLVER_ASSERT(mkr_weight > 0.0,
                        "'sqrt' will be NaN if the weight is less than 0.0.");
        mkr_weight = std::sqrt(mkr_weight);

        // Re-project Bundle into screen-space.
        MVector bnd_dir;
        status = bnd->getPos(bnd_mpos, frame, timeEvalMode);
        MMSOLVER_CHECK_MSTATUS(status);
        MPoint bnd_mpos_tmp(bnd_mpos);
        bnd_dir = bnd_mpos_tmp - cam_pos;
        bnd_dir.normalize();
        bnd_mpos = bnd_mpos * cameraWorldProjectionMatrix;
        bnd_mpos.cartesianize();
        // Convert to -0.5 to 0.5 range for 2D coordinates inside the
        // film back.
        double point_x = bnd_mpos[0] * 0.5;
        double point_y = bnd_mpos[1] * 0.5;

#if MMSOLVER_LENS_DISTORTION == 1 && MMSOLVER_LENS_DISTORTION_MAYA_DAG == 1
        auto markerFrameIndex = markerIndex + frameIndex;
        auto lensModel = ud->markerFrameToLensModelList[markerFrameIndex];
        if (lensModel) {
            double out_x = point_x;
            double out_y = point_y;
            lensModel->applyModelDistort(point_x, point_y, out_x, out_y);

            // Applying the lens distortion model to large input
            // values, creates NaN undistorted points.
            if (std::isfinite(out_x)) {
                point_x = out_x;
            }
            if (std::isfinite(out_y)) {
                point_y = out_y;
            }
        }
#endif

        // According to the Ceres solver 'circle_fit.cc'
        // example, using the 'sqrt' distance error function is a
        // bad idea as it will introduce non-linearities, we are
        // better off using something like 'x*x - y*y'. It would
        // be best to test this detail.
        const double dx = std::fabs(mkr_x - point_x) * imageWidth;
        const double dy = std::fabs(mkr_y - point_y) * imageWidth;

        auto errorIndex_x = i * ERRORS_PER_MARKER;
        auto errorIndex_y = errorIndex_x + 1;
        errors[errorIndex_x] = dx * mkr_weight;
        errors[errorIndex_y] = dy * mkr_weight;

        // 'ud->errorList' is the deviation shown to the user, it
        // should not have any loss functions or scaling applied to it.
        ud->errorList[errorIndex_x] = dx;
        ud->errorList[errorIndex_y] = dy;

        const double d =
            distance_2d(mkr_x, mkr_y, point_x, point_y) * imageWidth;
        ud->errorDistanceList[i] = d;
        error_avg += d;
        if (d > error_max) {
            error_max = d;
        }
        if (d < error_min) {
            error_min = d;
        }
        ++numberOfErrorsMeasured;
    }
    if (numberOfErrorsMeasured == 0) {
        error_max = 0.0;
        error_min = 0.0;
        error_avg = 0.0;
        MMSOLVER_MAYA_ERR("No Marker measurements were taken.");
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
        AttrPtr attr = ud->attrList.get_attr(attrIndex);

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
        double error =
            1.0 / std::fabs(mmmath::dot(straight_line_norm, new_line_norm));
#else
        double error =
            ((1.0 / gaussian(attrValue, stiffValue, stiffVariance)) - 1.0);
#endif

        ud->errorList[indexIntoErrorArray] = error * stiffWeight;
        errors[indexIntoErrorArray] = error * stiffWeight;
    }

    // Compute the smoothness values for the the attributes of the 'error'
    // array. Smoothness is an error weighting to the predicted next value that
    // is smooth.
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
        AttrPtr attr = ud->attrList.get_attr(attrIndex);

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
        double error =
            1.0 / std::fabs(mmmath::dot(straight_line_norm, new_line_norm));
#else
        double error =
            ((1.0 / gaussian(attrValue, smoothValue, smoothVariance)) - 1.0);
#endif

        ud->errorList[indexIntoErrorArray] = error * smoothWeight;
        errors[indexIntoErrorArray] = error * smoothWeight;
    }
}

void measureErrors_mmSceneGraph(const int numberOfErrors,
                                const int numberOfMarkerErrors,
                                const int numberOfAttrStiffnessErrors,
                                const int numberOfAttrSmoothnessErrors,
                                const std::vector<bool> &frameIndexEnable,
                                const std::vector<bool> &errorMeasurements,
                                const double imageWidth, double *errors,
                                SolverData *ud, double &error_avg,
                                double &error_max, double &error_min,
                                MStatus &status) {
    MMSOLVER_CORE_UNUSED(numberOfErrors);
    MMSOLVER_CORE_UNUSED(numberOfAttrStiffnessErrors);
    MMSOLVER_CORE_UNUSED(numberOfAttrSmoothnessErrors);
    MMSOLVER_CORE_UNUSED(status);

    // Evaluate Scene.
    ud->mmsgFlatScene.evaluate(ud->mmsgAttrDataBlock, ud->mmsgFrameList);

    auto num_points = ud->mmsgFlatScene.num_points();
    auto num_markers = ud->mmsgFlatScene.num_markers();
    auto num_frames = ud->mmsgFrameList.size();
    auto num_marker_lens_models = ud->lensModelList.size();
    MMSOLVER_CORE_UNUSED(num_points);
    MMSOLVER_CORE_UNUSED(num_markers);
    MMSOLVER_ASSERT(num_points == num_markers,
                    "MM Scene Graph points counts and markers must match to be "
                    "consistent.");

    auto out_point_list = ud->mmsgFlatScene.points();
    auto out_marker_list = ud->mmsgFlatScene.markers();
    MMSOLVER_ASSERT(
        out_marker_list.size() == out_point_list.size(),
        "MM Scene Graph Flat Scene points counts and markers must match to be "
        "consistent.");

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

        if (frameIndex != -1) {
            const Count32 enabledAttrs =
                countEnabledAttrsForMarkerToAttrToFrameRelationship(
                    markerIndex, frameIndex, ud->markerToAttrToFrameMatrix);
            if (enabledAttrs == 0) {
                continue;
            }
        }

        // Use pre-computed marker weight
        double mkr_weight = ud->markerWeightList[i];
        MMSOLVER_ASSERT(mkr_weight > 0.0,
                        "'sqrt' will be NaN if the weight is less than 0.0.");
        mkr_weight = std::sqrt(mkr_weight);

        auto mkrIndex_x = ((markerIndex * num_frames * 2) + (frameIndex * 2));
        auto mkrIndex_y = mkrIndex_x + 1;
        auto mkr_x = out_marker_list[mkrIndex_x];
        auto mkr_y = out_marker_list[mkrIndex_y];
        auto point_x = out_point_list[mkrIndex_x];
        auto point_y = out_point_list[mkrIndex_y];

#if MMSOLVER_LENS_DISTORTION == 1 && \
    MMSOLVER_LENS_DISTORTION_MM_SCENE_GRAPH == 1
        auto markerFrameIndex = markerIndex + frameIndex;
        auto lensModel = ud->markerFrameToLensModelList[markerFrameIndex];
        if (lensModel) {
            double out_x = point_x;
            double out_y = point_y;
            lensModel->applyModelDistort(point_x, point_y, out_x, out_y);

            // Applying the lens distortion model to large input
            // values, creates NaN undistorted points.
            if (std::isfinite(out_x)) {
                point_x = out_x;
            }
            if (std::isfinite(out_y)) {
                point_y = out_y;
            }
        }
#endif

        auto dx = std::fabs(mkr_x - point_x);
        auto dy = std::fabs(mkr_y - point_y);
        auto dx_pixels = dx * imageWidth;
        auto dy_pixels = dy * imageWidth;

        auto errorIndex_x = i * ERRORS_PER_MARKER;
        auto errorIndex_y = errorIndex_x + 1;
        errors[errorIndex_x] = dx_pixels * mkr_weight;
        errors[errorIndex_y] = dy_pixels * mkr_weight;

        // 'ud->errorList' is the deviation shown to the user, it
        // should not have any loss functions or scaling applied to it.
        ud->errorList[errorIndex_x] = dx_pixels;
        ud->errorList[errorIndex_y] = dy_pixels;

        const double d = std::sqrt((dx * dx) + (dy * dy)) * imageWidth;
        ud->errorDistanceList[i] = d;
        error_avg += d;
        if (d > error_max) {
            error_max = d;
        }
        if (d < error_min) {
            error_min = d;
        }
        ++numberOfErrorsMeasured;
    }
    if (numberOfErrorsMeasured == 0) {
        error_max = 0.0;
        error_min = 0.0;
        error_avg = 0.0;
        MMSOLVER_MAYA_ERR("No Marker measurements were taken.");
    } else {
        error_avg *= 1.0 / numberOfErrorsMeasured;
    }

    // TODO: Support stiffness and smoothness.
}

void measureErrors(const int numberOfErrors, const int numberOfMarkerErrors,
                   const int numberOfAttrStiffnessErrors,
                   const int numberOfAttrSmoothnessErrors,
                   const std::vector<bool> &frameIndexEnable,
                   const std::vector<bool> &errorMeasurements,
                   const double imageWidth, double *errors, SolverData *ud,
                   double &error_avg, double &error_max, double &error_min,
                   MStatus &status) {
    error_avg = 0.0;
    error_max = -0.0;
    error_min = std::numeric_limits<double>::max();

    MMSOLVER_ASSERT(ud->errorToMarkerList.size() > 0,
                    "Must have markers to measure.");
    MMSOLVER_ASSERT(ud->frameList.size() > 0,
                    "Must have frames to measure markers on.");

    const SceneGraphMode sceneGraphMode = ud->solverOptions->sceneGraphMode;
    if (sceneGraphMode == SceneGraphMode::kMayaDag) {
        measureErrors_mayaDag(
            numberOfErrors, numberOfMarkerErrors, numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors, frameIndexEnable, errorMeasurements,
            imageWidth, errors, ud, error_avg, error_max, error_min, status);
    } else if (sceneGraphMode == SceneGraphMode::kMMSceneGraph) {
        measureErrors_mmSceneGraph(
            numberOfErrors, numberOfMarkerErrors, numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors, frameIndexEnable, errorMeasurements,
            imageWidth, errors, ud, error_avg, error_max, error_min, status);
    }

    // Changes the errors to be scaled by the loss function.
    // This will reduce the affect outliers have on the solve.
    if (ud->solverOptions->solverSupportsRobustLoss) {
        // TODO: Scale the jacobian by the loss function too?
        applyLossFunctionToErrors(numberOfErrors, errors,
                                  ud->solverOptions->robustLossType,
                                  ud->solverOptions->robustLossScale);
    }

    MMSOLVER_CHECK(error_max >= error_min,
                   "Maximum and minimum values should be consistent."
                       << " error_max=" << error_max
                       << " error_min=" << error_min);
    if (error_max >= error_min) {
        ud->internalErrorDetected = true;
    }
}

// Clean up #define
#undef FORCE_TRIGGER_EVAL

}  // namespace mmsolver
