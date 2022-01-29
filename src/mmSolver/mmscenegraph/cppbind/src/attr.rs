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

use crate::cxxbridge::ffi::AttrId as BindAttrId;
use crate::cxxbridge::ffi::AttrType as BindAttrType;
use crate::cxxbridge::ffi::CameraAttrIds as BindCameraAttrIds;
use crate::cxxbridge::ffi::MarkerAttrIds as BindMarkerAttrIds;
use crate::cxxbridge::ffi::Rotate3DAttrIds as BindRotate3DAttrIds;
use crate::cxxbridge::ffi::Scale3DAttrIds as BindScale3DAttrIds;
use crate::cxxbridge::ffi::Translate3DAttrIds as BindTranslate3DAttrIds;
use mmscenegraph_rust::attr::AttrId as CoreAttrId;

pub fn bind_to_core_attr_id(value: BindAttrId) -> CoreAttrId {
    match value.attr_type {
        BindAttrType::Static => CoreAttrId::Static(value.index),
        BindAttrType::AnimDense => CoreAttrId::AnimDense(value.index),
        BindAttrType::None => CoreAttrId::None,
        _ => CoreAttrId::None,
    }
}

pub fn core_to_bind_attr_id(value: CoreAttrId) -> BindAttrId {
    match value {
        CoreAttrId::Static(index) => BindAttrId {
            attr_type: BindAttrType::Static,
            index,
        },
        CoreAttrId::AnimDense(index) => BindAttrId {
            attr_type: BindAttrType::AnimDense,
            index,
        },
        _ => BindAttrId {
            attr_type: BindAttrType::None,
            index: 0,
        },
    }
}

pub fn bind_to_core_translate_3d_attr_ids(
    bind_attrs: BindTranslate3DAttrIds,
) -> (CoreAttrId, CoreAttrId, CoreAttrId) {
    (
        bind_to_core_attr_id(bind_attrs.tx),
        bind_to_core_attr_id(bind_attrs.ty),
        bind_to_core_attr_id(bind_attrs.tz),
    )
}

pub fn bind_to_core_rotate_3d_attr_ids(
    bind_attrs: BindRotate3DAttrIds,
) -> (CoreAttrId, CoreAttrId, CoreAttrId) {
    (
        bind_to_core_attr_id(bind_attrs.rx),
        bind_to_core_attr_id(bind_attrs.ry),
        bind_to_core_attr_id(bind_attrs.rz),
    )
}

pub fn bind_to_core_scale_3d_attr_ids(
    bind_attrs: BindScale3DAttrIds,
) -> (CoreAttrId, CoreAttrId, CoreAttrId) {
    (
        bind_to_core_attr_id(bind_attrs.sx),
        bind_to_core_attr_id(bind_attrs.sy),
        bind_to_core_attr_id(bind_attrs.sz),
    )
}

pub fn bind_to_core_camera_attr_ids(
    bind_attrs: BindCameraAttrIds,
) -> (CoreAttrId, CoreAttrId, CoreAttrId) {
    (
        bind_to_core_attr_id(bind_attrs.sensor_width),
        bind_to_core_attr_id(bind_attrs.sensor_height),
        bind_to_core_attr_id(bind_attrs.focal_length),
    )
}

pub fn bind_to_core_marker_attr_ids(
    bind_attrs: BindMarkerAttrIds,
) -> (CoreAttrId, CoreAttrId, CoreAttrId) {
    (
        bind_to_core_attr_id(bind_attrs.tx),
        bind_to_core_attr_id(bind_attrs.ty),
        bind_to_core_attr_id(bind_attrs.weight),
    )
}
