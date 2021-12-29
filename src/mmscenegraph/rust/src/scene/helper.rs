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

use crate::attr::datablock::AttrDataBlock;
use crate::constant::Real;
use crate::math::rotate::euler::RotateOrder;
use crate::node::bundle::BundleNode;
use crate::node::camera::CameraNode;
use crate::node::marker::MarkerNode;
use crate::node::transform::TransformNode;
use crate::scene::graph::SceneGraph;

pub fn create_static_transform(
    sg: &mut SceneGraph,
    attrdb: &mut AttrDataBlock,
    translate: (Real, Real, Real),
    rotate: (Real, Real, Real),
    scale: (Real, Real, Real),
    rotate_order: RotateOrder,
) -> TransformNode {
    let (tx, ty, tz) = translate;
    let attr_tx = attrdb.create_attr_static(tx);
    let attr_ty = attrdb.create_attr_static(ty);
    let attr_tz = attrdb.create_attr_static(tz);
    let translate_attrs = (attr_tx, attr_ty, attr_tz);

    let (rx, ry, rz) = rotate;
    let attr_rx = attrdb.create_attr_static(rx);
    let attr_ry = attrdb.create_attr_static(ry);
    let attr_rz = attrdb.create_attr_static(rz);
    let rotate_attrs = (attr_rx, attr_ry, attr_rz);

    let (sx, sy, sz) = scale;
    let attr_sx = attrdb.create_attr_static(sx);
    let attr_sy = attrdb.create_attr_static(sy);
    let attr_sz = attrdb.create_attr_static(sz);
    let scale_attrs = (attr_sx, attr_sy, attr_sz);

    sg.create_transform_node(translate_attrs, rotate_attrs, scale_attrs, rotate_order)
}

pub fn create_static_marker(
    sg: &mut SceneGraph,
    attrdb: &mut AttrDataBlock,
    translate: (Real, Real),
    weight: Real,
) -> MarkerNode {
    let (tx, ty) = translate;
    let attr_tx = attrdb.create_attr_static(tx);
    let attr_ty = attrdb.create_attr_static(ty);
    let attr_weight = attrdb.create_attr_static(weight);
    let mkr = sg.create_marker_node((attr_tx, attr_ty), attr_weight);
    mkr
}

pub fn create_static_bundle(
    sg: &mut SceneGraph,
    attrdb: &mut AttrDataBlock,
    translate: (Real, Real, Real),
    rotate: (Real, Real, Real),
    scale: (Real, Real, Real),
    rotate_order: RotateOrder,
) -> BundleNode {
    let (tx, ty, tz) = translate;
    let attr_tx = attrdb.create_attr_static(tx);
    let attr_ty = attrdb.create_attr_static(ty);
    let attr_tz = attrdb.create_attr_static(tz);
    let translate_attrs = (attr_tx, attr_ty, attr_tz);

    let (rx, ry, rz) = rotate;
    let attr_rx = attrdb.create_attr_static(rx);
    let attr_ry = attrdb.create_attr_static(ry);
    let attr_rz = attrdb.create_attr_static(rz);
    let rotate_attrs = (attr_rx, attr_ry, attr_rz);

    let (sx, sy, sz) = scale;
    let attr_sx = attrdb.create_attr_static(sx);
    let attr_sy = attrdb.create_attr_static(sy);
    let attr_sz = attrdb.create_attr_static(sz);
    let scale_attrs = (attr_sx, attr_sy, attr_sz);

    sg.create_bundle_node(translate_attrs, rotate_attrs, scale_attrs, rotate_order)
}

pub fn create_static_camera(
    sg: &mut SceneGraph,
    attrdb: &mut AttrDataBlock,
    translate: (Real, Real, Real),
    rotate: (Real, Real, Real),
    scale: (Real, Real, Real),
    sensor: (Real, Real),
    focal_length: Real,
    rotate_order: RotateOrder,
) -> CameraNode {
    let (tx, ty, tz) = translate;
    let attr_tx = attrdb.create_attr_static(tx);
    let attr_ty = attrdb.create_attr_static(ty);
    let attr_tz = attrdb.create_attr_static(tz);
    let translate_attrs = (attr_tx, attr_ty, attr_tz);

    let (rx, ry, rz) = rotate;
    let attr_rx = attrdb.create_attr_static(rx);
    let attr_ry = attrdb.create_attr_static(ry);
    let attr_rz = attrdb.create_attr_static(rz);
    let rotate_attrs = (attr_rx, attr_ry, attr_rz);

    let (sx, sy, sz) = scale;
    let attr_sx = attrdb.create_attr_static(sx);
    let attr_sy = attrdb.create_attr_static(sy);
    let attr_sz = attrdb.create_attr_static(sz);
    let scale_attrs = (attr_sx, attr_sy, attr_sz);

    let (sensor_width, sensor_height) = sensor;
    let attr_sensor_width = attrdb.create_attr_static(sensor_width);
    let attr_sensor_height = attrdb.create_attr_static(sensor_height);
    let attr_focal_length = attrdb.create_attr_static(focal_length);

    sg.create_camera_node(
        translate_attrs,
        rotate_attrs,
        scale_attrs,
        attr_sensor_width,
        attr_sensor_height,
        attr_focal_length,
        rotate_order,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_transform_node() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_transform_nodes(), 0);
        let _tfm = create_static_transform(
            &mut sg,
            &mut attrdb,
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            RotateOrder::XYZ,
        );
        assert_eq!(sg.num_transform_nodes(), 1);
    }

    #[test]
    fn test_create_bundle_node() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_bundle_nodes(), 0);
        let _bnd = create_static_bundle(
            &mut sg,
            &mut attrdb,
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            RotateOrder::XYZ,
        );
        assert_eq!(sg.num_bundle_nodes(), 1);
    }

    #[test]
    fn test_create_camera_node() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_camera_nodes(), 0);
        let _cam = create_static_camera(
            &mut sg,
            &mut attrdb,
            (1.0, 10.0, -1.0),
            (-10.0, 5.0, 1.0),
            (1.0, 1.0, 1.0),
            (36.0, 24.0),
            50.0,
            RotateOrder::ZXY,
        );
        assert_eq!(sg.num_camera_nodes(), 1);
    }

    #[test]
    fn test_create_marker_node() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_marker_nodes(), 0);
        let _mkr = create_static_marker(&mut sg, &mut attrdb, (0.5, 0.5), 1.0);
        assert_eq!(sg.num_marker_nodes(), 1);
    }
}
