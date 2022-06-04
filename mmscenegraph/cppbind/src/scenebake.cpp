/*
 * Copyright (C) 2020, 2021 David Cattermole.
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

#include <mmscenegraph/_cxxbridge.h>
#include <mmscenegraph/evaluationobjects.h>
#include <mmscenegraph/flatscene.h>
#include <mmscenegraph/scenebake.h>
#include <mmscenegraph/scenegraph.h>

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
FlatScene bake_scene_graph(SceneGraph &sg,
                           EvaluationObjects &eval_objects) noexcept {
    auto sg_inner = sg.get_inner();
    auto eval_objects_inner = eval_objects.get_inner();
    auto box_shim_flat_scene =
        shim_bake_scene_graph(sg_inner, eval_objects_inner);
    auto flat_scene = FlatScene(std::move(box_shim_flat_scene));
    return flat_scene;
}

}  // namespace mmscenegraph
