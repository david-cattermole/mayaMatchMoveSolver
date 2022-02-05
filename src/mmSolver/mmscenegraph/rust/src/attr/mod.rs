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

pub mod animdense;
pub mod datablock;
pub mod staticattr;

use crate::constant::AttrIndex;

#[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
pub enum AttrId {
    AnimDense(AttrIndex),
    Static(AttrIndex),
    None,
}

#[derive(Debug, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
pub struct AttrTransformIds {
    pub tx: AttrId,
    pub ty: AttrId,
    pub tz: AttrId,
    //
    pub rx: AttrId,
    pub ry: AttrId,
    pub rz: AttrId,
    //
    pub sx: AttrId,
    pub sy: AttrId,
    pub sz: AttrId,
}

#[derive(Debug, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
pub struct AttrCameraIds {
    pub sensor_width: AttrId,
    pub sensor_height: AttrId,
    pub focal_length: AttrId,
    pub lens_offset_x: AttrId,
    pub lens_offset_y: AttrId,
    pub near_clip_plane: AttrId,
    pub far_clip_plane: AttrId,
    pub camera_scale: AttrId,
}

#[derive(Debug, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
pub struct AttrMarkerIds {
    pub tx: AttrId,
    pub ty: AttrId,
    pub weight: AttrId,
}
