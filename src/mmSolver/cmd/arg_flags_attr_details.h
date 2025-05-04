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
 */

#ifndef MM_SOLVER_ARG_FLAGS_ATTR_DETAILS_H
#define MM_SOLVER_ARG_FLAGS_ATTR_DETAILS_H

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MArgParser.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// Internal Objects
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/utilities/debug_utils.h"

// Attribute (Detail) Stiffness. As of v0.4.0 this feature is
// deprecated.
#define STIFFNESS_FLAG "-asf"
#define STIFFNESS_FLAG_LONG "-attrStiffness"

// Attribute (Detail) Smoothness. As of v0.4.0 this feature is
// deprecated.
#define SMOOTHNESS_FLAG "-asm"
#define SMOOTHNESS_FLAG_LONG "-attrSmoothness"

namespace mmsolver {

// Add flags for attribute details to the command syntax.
void createAttributeDetailsSyntax(MSyntax &syntax);

// Parse arguments into attribute details.
MStatus parseAttributeDetailsArguments(const MArgDatabase &argData,
                                       const AttrList &attrList,
                                       StiffAttrsPtrList &out_stiffAttrsList,
                                       SmoothAttrsPtrList &out_smoothAttrsList);

}  // namespace mmsolver

#endif  // MM_SOLVER_ARG_FLAGS_ATTR_DETAILS_H
