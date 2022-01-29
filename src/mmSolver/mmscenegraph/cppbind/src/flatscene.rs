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

use crate::attrdatablock::ShimAttrDataBlock;
use mmscenegraph_rust::constant::FrameValue as CoreFrameValue;
use mmscenegraph_rust::constant::Real as CoreReal;
use mmscenegraph_rust::scene::flat::FlatScene as CoreFlatScene;

pub struct ShimFlatScene {
    inner: CoreFlatScene,
}

impl ShimFlatScene {
    pub fn new(core_flat_scene: CoreFlatScene) -> Self {
        Self {
            inner: core_flat_scene,
        }
    }

    pub fn get_inner(&self) -> &CoreFlatScene {
        &self.inner
    }

    pub fn markers(&self) -> &[CoreReal] {
        &self.inner.markers()
    }

    pub fn points(&self) -> &[CoreReal] {
        &self.inner.points()
    }

    pub fn deviations(&self) -> &[CoreReal] {
        &self.inner.deviations()
    }

    pub fn num_markers(&self) -> usize {
        self.inner.num_markers()
    }

    pub fn num_points(&self) -> usize {
        self.inner.num_points()
    }

    pub fn num_deviations(&self) -> usize {
        self.inner.num_deviations()
    }

    pub fn evaluate(
        &mut self,
        attrdb: &ShimAttrDataBlock,
        frame_list: &[CoreFrameValue],
    ) {
        self.inner.evaluate(attrdb.get_inner(), frame_list)
    }
}

pub fn shim_create_flat_scene_box() -> Box<ShimFlatScene> {
    println!("shim_create_flat_scene_box()");
    let bnd_ids = Vec::new();
    let cam_ids = Vec::new();
    let mkr_ids = Vec::new();
    let mkr_cam_indices = Vec::new();
    let mkr_bnd_indices = Vec::new();
    let tfm_attr_list = Vec::new();
    let rotate_order_list = Vec::new();
    let cam_attr_list = Vec::new();
    let mkr_attr_list = Vec::new();
    let tfm_node_ids = Vec::new();
    let tfm_node_indices = Vec::new();
    let tfm_node_parent_indices = Vec::new();
    let core_flat_scene = CoreFlatScene::new(
        bnd_ids,
        cam_ids,
        mkr_ids,
        mkr_cam_indices,
        mkr_bnd_indices,
        tfm_attr_list,
        rotate_order_list,
        cam_attr_list,
        mkr_attr_list,
        tfm_node_ids,
        tfm_node_indices,
        tfm_node_parent_indices,
    );
    Box::new(ShimFlatScene::new(core_flat_scene))
}
