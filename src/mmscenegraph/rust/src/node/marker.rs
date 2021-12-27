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

use crate::attr::AttrId;
use crate::constant::Real;
use crate::node::traits::NodeCanTransform2D;
use crate::node::traits::NodeCanTranslate2D;
use crate::node::traits::NodeHasId;
use crate::node::traits::NodeHasWeight;
use crate::node::NodeId;

#[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
pub struct MarkerNode {
    id: NodeId,
    attr_tx: AttrId,
    attr_ty: AttrId,
    attr_weight: AttrId,
}

impl Default for MarkerNode {
    fn default() -> Self {
        Self {
            id: NodeId::None,
            attr_tx: AttrId::None,
            attr_ty: AttrId::None,
            attr_weight: AttrId::None,
        }
    }
}

impl NodeHasId for MarkerNode {
    fn get_id(&self) -> NodeId {
        self.id
    }

    fn set_id(&mut self, value: NodeId) {
        self.id = value;
    }
}

impl NodeCanTranslate2D for MarkerNode {
    fn get_attr_tx(&self) -> AttrId {
        self.attr_tx
    }
    fn get_attr_ty(&self) -> AttrId {
        self.attr_ty
    }
    fn set_attr_tx(&mut self, attr: AttrId) {
        self.attr_tx = attr;
    }
    fn set_attr_ty(&mut self, attr: AttrId) {
        self.attr_ty = attr;
    }
}

impl NodeHasWeight for MarkerNode {
    fn get_attr_weight(&self) -> AttrId {
        self.attr_weight
    }
    fn set_attr_weight(&mut self, attr: AttrId) {
        self.attr_weight = attr;
    }
}

impl NodeCanTransform2D for MarkerNode {}
