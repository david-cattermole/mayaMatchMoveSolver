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
 * Lens model adjustment.
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_LENS_MODEL_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_LENS_MODEL_H

#include "adjust_data.h"
#include "mmSolver/lens/lens_model.h"
#include "mmSolver/mayahelper/maya_attr.h"

MStatus setLensModelAttributeValue(std::shared_ptr<LensModel> &lensModel,
                                   const AttrSolverType attrType,
                                   const double value);

MStatus constructLensModelList(
    const CameraPtrList &cameraList, const MarkerPtrList &markerList,
    const AttrPtrList &attrList, const MTimeArray &frameList,
    std::vector<std::shared_ptr<LensModel>> &out_markerFrameToLensModelList,
    std::vector<std::shared_ptr<LensModel>> &out_attrFrameToLensModelList,
    std::vector<std::shared_ptr<LensModel>> &out_lensModelList);

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_LENS_MODEL_H
