//
// Copyright (C) 2020, 2021 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// mmSolver is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
// ====================================================================
//

use crate::evaluationobjects::ShimEvaluationObjects;
use crate::flatscene::ShimFlatScene;
use crate::scenegraph::ShimSceneGraph;
use mmscenegraph_rust::scene::bake::bake_scene_graph as core_bake_scene_graph;

pub fn shim_bake_scene_graph(
    sg: &Box<ShimSceneGraph>,
    eval_objects: &Box<ShimEvaluationObjects>,
) -> Box<ShimFlatScene> {
    let core_flat_scene =
        core_bake_scene_graph(sg.get_inner(), eval_objects.get_inner());
    let shim_flat_scene = ShimFlatScene::new(core_flat_scene);
    Box::new(shim_flat_scene)
}
