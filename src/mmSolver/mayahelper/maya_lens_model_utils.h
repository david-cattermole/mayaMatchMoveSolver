/*
 * Copyright (C) 2022 David Cattermole.
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
 * Lens model utilities.
 */

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_LENS_MODEL_H
#define MM_SOLVER_MAYA_HELPER_MAYA_LENS_MODEL_H

// STL
#include <memory>
#include <vector>

// Maya
#include <maya/MTimeArray.h>

// MM Solver
#include <mmlens/lens_model.h>

#include "mmSolver/core/frame_list.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_list.h"

namespace mmsolver {

MStatus getLensModelFromCamera(
    const CameraPtr &camera, std::shared_ptr<mmlens::LensModel> &out_lensModel);

MStatus setLensModelAttributeValue(
    std::shared_ptr<mmlens::LensModel> &lensModel,
    const AttrSolverType attrType, const double value);

MStatus constructLensModelList(
    const CameraPtrList &cameraList, const MarkerList &markerList,
    const AttrList &attrList, const FrameList &frameList,
    std::vector<std::shared_ptr<mmlens::LensModel>>
        &out_markerFrameToLensModelList,
    std::vector<std::shared_ptr<mmlens::LensModel>>
        &out_attrFrameToLensModelList,
    std::vector<std::shared_ptr<mmlens::LensModel>> &out_lensModelList);

}  // namespace mmsolver

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_LENS_MODEL_H
