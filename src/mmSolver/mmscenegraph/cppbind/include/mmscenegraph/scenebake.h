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

#ifndef MM_SOLVER_MM_SCENE_GRAPH_SCENE_BAKE_H
#define MM_SOLVER_MM_SCENE_GRAPH_SCENE_BAKE_H

#include <memory>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "scenebake.h"
#include "flatscene.h"
#include "scenegraph.h"
#include "evaluationobjects.h"

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
FlatScene
bake_scene_graph(
    SceneGraph &sg,
    EvaluationObjects &solve_objects
) noexcept;

} // namespace mmscenegraph

#endif  // MM_SOLVER_MM_SCENE_GRAPH_SCENE_BAKE_H