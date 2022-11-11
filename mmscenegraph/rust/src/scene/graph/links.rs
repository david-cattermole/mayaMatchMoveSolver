//
// Copyright (C) 2020, 2021, 2022 David Cattermole.
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

use crate::node::NodeId;

#[derive(Debug, Clone)]
pub struct SceneLinks {
    mkr_to_cam_node_ids: Vec<NodeId>,
    mkr_to_bnd_node_ids: Vec<NodeId>,
}

impl SceneLinks {
    pub fn new() -> SceneLinks {
        SceneLinks {
            mkr_to_cam_node_ids: Vec::<NodeId>::new(),
            mkr_to_bnd_node_ids: Vec::<NodeId>::new(),
        }
    }

    pub fn clear(&mut self) {
        self.mkr_to_cam_node_ids.clear();
        self.mkr_to_bnd_node_ids.clear();
    }

    pub fn add_marker_to_camera_node_ids(&mut self, node_id: NodeId) {
        self.mkr_to_cam_node_ids.push(node_id);
    }

    pub fn add_marker_to_bundle_node_ids(&mut self, node_id: NodeId) {
        self.mkr_to_bnd_node_ids.push(node_id);
    }

    pub fn link_marker_to_camera(
        &mut self,
        mkr_node_id: NodeId,
        cam_node_id: NodeId,
    ) -> bool {
        let mkr_index = match mkr_node_id {
            NodeId::Marker(index) => index,
            _ => return false,
        };
        match cam_node_id {
            NodeId::Camera(_) => {
                self.mkr_to_cam_node_ids[mkr_index] = cam_node_id
            }
            _ => return false,
        };
        return true;
    }

    pub fn link_marker_to_bundle(
        &mut self,
        mkr_node_id: NodeId,
        bnd_node_id: NodeId,
    ) -> bool {
        let mkr_index = match mkr_node_id {
            NodeId::Marker(index) => index,
            _ => return false,
        };
        match bnd_node_id {
            NodeId::Bundle(_) => {
                self.mkr_to_bnd_node_ids[mkr_index] = bnd_node_id
            }
            _ => return false,
        };
        return true;
    }

    pub fn get_camera_node_id_from_marker_node_id(
        &self,
        node_id: NodeId,
    ) -> Option<NodeId> {
        match node_id {
            NodeId::Marker(index) => Some(self.mkr_to_cam_node_ids[index]),
            _ => None,
        }
    }

    pub fn get_bundle_node_id_from_marker_node_id(
        &self,
        node_id: NodeId,
    ) -> Option<NodeId> {
        match node_id {
            NodeId::Marker(index) => Some(self.mkr_to_bnd_node_ids[index]),
            _ => None,
        }
    }
}
