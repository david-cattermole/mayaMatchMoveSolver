/*
 * Copyright (C) 2023 David Cattermole.
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

#ifndef MM_SOLVER_RENDER_OPS_SCENE_UTILS_H
#define MM_SOLVER_RENDER_OPS_SCENE_UTILS_H

// Maya
#include <maya/M3dView.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MItDag.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MSelectionList.h>
#include <maya/MShaderManager.h>
#include <maya/MStateManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/data/BackgroundStyle.h"

namespace mmsolver {
namespace render {

enum class DrawObjects : short {
    kNoOverride = 0,
    kAllImagePlanes,
    kOnlyCameraBackgroundImagePlanes,
    kOnlyNamedLayerObjects,
    kDrawObjectsCount,
};

MStatus only_named_layer_objects(MObject &layer_node,
                                 MSelectionList &out_selection_list);

MStatus add_all_image_planes(MSelectionList &out_selection_list);

const MSelectionList *find_draw_objects(const DrawObjects draw_objects,
                                        const MString &layer_name,
                                        MSelectionList &out_selection_list);

bool set_background_clear_operation(
    const BackgroundStyle background_style, const uint32_t clear_mask,
    MHWRender::MClearOperation &out_clear_operation);

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_OPS_SCENE_UTILS_H
