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
 * Set the parameters for the Maya DAG or MM Scene Graph to have an
 * effect.
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

// MM Scene Graph
#include <mmscenegraph/mmscenegraph.h>

// MM Solver
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

#include "adjust_base.h"
#include "adjust_data.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_lens_model_utils.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsg = mmscenegraph;

namespace mmsolver {

// Set Parameter values
MStatus setParameters_mayaDag(const int numberOfParameters,
                              const double *parameters, SolverData *ud) {
    MStatus status = MS::kSuccess;

    uint32_t mayaAttrsSet = 0;
    uint32_t lensModelAttrsSet = 0;
    MTime currentFrame = MAnimControl::currentTime();
    for (int i = 0; i < numberOfParameters; ++i) {
        const IndexPair attrPair = ud->paramToAttrList[i];
        auto attrIndex = attrPair.first;
        auto frameIndex = attrPair.second;

        AttrPtr attr = ud->attrList[attrPair.first];

        const double offset = attr->getOffsetValue();
        const double scale = attr->getScaleValue();
        const double xmin = attr->getMinimumValue();
        const double xmax = attr->getMaximumValue();
        const double solver_value = parameters[i];

        double real_value = solver_value;
        if (ud->solverOptions->solverSupportsParameterBounds) {
            real_value = parameterBoundFromInternalToExternal(
                solver_value, xmin, xmax, offset, scale);
        }

#if MMSOLVER_LENS_DISTORTION == 1 && MMSOLVER_LENS_DISTORTION_MAYA_DAG == 1
        const auto object_type = attr->getObjectType();
        if (object_type == ObjectType::kLens) {
            auto num_frames = ud->frameList.length();
            auto solverAttrType = attr->getSolverAttrType();
            if (frameIndex != -1) {
                // Animated attribute.
                auto lensModel =
                    ud->attrFrameToLensModelList[attrIndex + frameIndex];
                status = mmsolver::setLensModelAttributeValue(
                    lensModel, solverAttrType, real_value);
                CHECK_MSTATUS_AND_RETURN_IT(status);
            } else {
                // Static attribute.
                for (int j = 0; j < num_frames; ++j) {
                    auto lensModel =
                        ud->attrFrameToLensModelList[attrIndex + j];
                    status = mmsolver::setLensModelAttributeValue(
                        lensModel, solverAttrType, real_value);
                    CHECK_MSTATUS_AND_RETURN_IT(status);
                }
            }
            lensModelAttrsSet += 1;
            continue;
        }
#endif

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            frame = ud->frameList[attrPair.second];
        }

        mayaAttrsSet += 1;
        status =
            attr->setValue(real_value, frame, *ud->dgmod, *ud->curveChange);
        if (status != MS::kSuccess) {
            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            MMSOLVER_MAYA_ERR(
                "setParameters (Maya DAG) was given an invalid value to set:"
                << " frame=" << frame << " attr name=" << attr_name_char
                << " solver value=" << solver_value
                << " bound value=" << real_value << " offset=" << offset
                << " scale=" << scale << " min=" << xmin << " max=" << xmax);

            break;
        }
    }

    if (mayaAttrsSet > 0) {
        // Commit changed data into Maya
        ud->dgmod->doIt();

        // Invalidate the Camera Matrix cache.
        //
        // In future we might be able to auto-detect if the camera
        // will change based on the current solve and not invalidate
        // the cache but for now we cannot take the risk of an
        // incorrect solve; we clear the cache.
        for (auto i = 0; i < ud->cameraList.size(); ++i) {
            ud->cameraList[i]->clearAttrValueCache();
        }
    }

    return status;
}

MStatus setParameters_mmSceneGraph(const int numberOfParameters,
                                   const double *parameters, SolverData *ud) {
    MStatus status = MS::kSuccess;

    uint32_t lensModelAttrsSet = 0;
    auto num_frames = ud->mmsgFrameList.size();
    for (int i = 0; i < numberOfParameters; ++i) {
        const IndexPair attrPair = ud->paramToAttrList[i];
        auto attrIndex = attrPair.first;
        auto frameIndex = attrPair.second;

        AttrPtr attr = ud->attrList[attrIndex];

        const double offset = attr->getOffsetValue();
        const double scale = attr->getScaleValue();
        const double xmin = attr->getMinimumValue();
        const double xmax = attr->getMaximumValue();
        // The solver value is used inside the solver to compute the
        // result, but is not the true value that will be set on the
        // attribute at the end of the solve.
        const double solver_value = parameters[i];

        double real_value = solver_value;
        if (ud->solverOptions->solverSupportsParameterBounds) {
            real_value = parameterBoundFromInternalToExternal(
                solver_value, xmin, xmax, offset, scale);
        }

#if MMSOLVER_LENS_DISTORTION == 1 && \
    MMSOLVER_LENS_DISTORTION_MM_SCENE_GRAPH == 1
        const auto object_type = attr->getObjectType();
        if (object_type == ObjectType::kLens) {
            auto solverAttrType = attr->getSolverAttrType();
            if (frameIndex != -1) {
                // Animated attribute.
                auto lensModel =
                    ud->attrFrameToLensModelList[attrIndex + frameIndex];
                status = mmsolver::setLensModelAttributeValue(
                    lensModel, solverAttrType, real_value);
                CHECK_MSTATUS_AND_RETURN_IT(status);
            } else {
                // Static attribute.
                for (int j = 0; j < num_frames; ++j) {
                    auto lensModel =
                        ud->attrFrameToLensModelList[attrIndex + j];
                    status = mmsolver::setLensModelAttributeValue(
                        lensModel, solverAttrType, real_value);
                    CHECK_MSTATUS_AND_RETURN_IT(status);
                }
            }
            lensModelAttrsSet += 1;
            continue;
        }
#endif

        mmsg::FrameValue frame = 0;
        if (frameIndex != -1) {
            frame = ud->mmsgFrameList[frameIndex];
        }

        mmsg::AttrId attrId = ud->mmsgAttrIdList[attrIndex];
        auto ok =
            ud->mmsgAttrDataBlock.set_attr_value(attrId, frame, real_value);
        if (!ok) {
            status = MS::kFailure;

            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            MMSOLVER_MAYA_ERR(
                "setParameters (MMSG) was given an invalid value to set:"
                << " attr name=" << attr_name_char
                << " solver value=" << solver_value
                << " bound value=" << real_value << " offset=" << offset
                << " scale=" << scale << " min=" << xmin << " max=" << xmax);
            break;
        }
    }

    return status;
}

// Set Parameter values
MStatus setParameters(const int numberOfParameters, const double *parameters,
                      SolverData *ud) {
    MStatus status = MS::kSuccess;

    const SceneGraphMode sceneGraphMode = ud->solverOptions->sceneGraphMode;
    if (sceneGraphMode == SceneGraphMode::kMayaDag) {
        status = setParameters_mayaDag(numberOfParameters, parameters, ud);
    } else if (sceneGraphMode == SceneGraphMode::kMMSceneGraph) {
        status = setParameters_mmSceneGraph(numberOfParameters, parameters, ud);
    } else {
        MMSOLVER_MAYA_ERR("setParameters failed, invalid SceneGraphMode: "
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

}  // namespace mmsolver
