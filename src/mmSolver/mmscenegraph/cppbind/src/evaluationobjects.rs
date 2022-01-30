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

use crate::cxxbridge::ffi::BundleNode as BindBundleNode;
use crate::cxxbridge::ffi::CameraNode as BindCameraNode;
use crate::cxxbridge::ffi::MarkerNode as BindMarkerNode;
use crate::node::bind_to_core_bundle_node;
use crate::node::bind_to_core_camera_node;
use crate::node::bind_to_core_marker_node;
use mmscenegraph_rust::scene::evaluationobjects::EvaluationObjects as CoreEvaluationObjects;

#[derive(Debug, Clone)]
pub struct ShimEvaluationObjects {
    inner: CoreEvaluationObjects,
}

impl ShimEvaluationObjects {
    fn new() -> Self {
        Self {
            inner: CoreEvaluationObjects::new(),
        }
    }

    pub fn get_inner(&self) -> &CoreEvaluationObjects {
        &self.inner
    }

    pub fn clear_all(&mut self) {
        self.inner.clear_all()
    }

    pub fn clear_bundles(&mut self) {
        self.inner.clear_bundles()
    }

    pub fn clear_cameras(&mut self) {
        self.inner.clear_cameras()
    }

    pub fn clear_markers(&mut self) {
        self.inner.clear_markers()
    }

    pub fn num_bundles(&self) -> usize {
        self.inner.num_bundles()
    }

    pub fn num_cameras(&self) -> usize {
        self.inner.num_cameras()
    }

    pub fn num_markers(&self) -> usize {
        self.inner.num_markers()
    }

    pub fn add_bundle(&mut self, bind_node: &BindBundleNode) {
        let core_node = bind_to_core_bundle_node(*bind_node);
        self.inner.add_bundle(core_node);
    }

    pub fn add_camera(&mut self, bind_node: &BindCameraNode) {
        let core_node = bind_to_core_camera_node(*bind_node);
        self.inner.add_camera(core_node);
    }

    pub fn add_marker(&mut self, bind_node: &BindMarkerNode) {
        let core_node = bind_to_core_marker_node(*bind_node);
        self.inner.add_marker(core_node);
    }
}

pub fn shim_create_evaluation_objects_box() -> Box<ShimEvaluationObjects> {
    Box::new(ShimEvaluationObjects::new())
}
