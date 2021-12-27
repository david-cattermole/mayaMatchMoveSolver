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

#[macro_use]
extern crate approx;

use nalgebra as na;

use mmscenegraph_rust::constant::Matrix14;
use mmscenegraph_rust::constant::Matrix44;
use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::math::camera::get_projection_matrix;
use mmscenegraph_rust::math::dag::compute_matrices;
use mmscenegraph_rust::math::dag::compute_matrix;
use mmscenegraph_rust::math::dag::compute_projection_matrix;
use mmscenegraph_rust::math::dag::compute_world_matrices;
use mmscenegraph_rust::math::reprojection::reproject;
use mmscenegraph_rust::math::reprojection::reproject_as_normalised_coord;
use mmscenegraph_rust::math::rotate::euler::RotateOrder;
use mmscenegraph_rust::math::transform::calculate_matrix;
use mmscenegraph_rust::math::transform::multiply;
use mmscenegraph_rust::math::transform::Transform;
use mmscenegraph_rust::node::bundle::BundleNode;
use mmscenegraph_rust::node::camera::CameraNode;
use mmscenegraph_rust::node::marker::MarkerNode;
use mmscenegraph_rust::node::traits::NodeCanTransform2D;
use mmscenegraph_rust::node::traits::NodeCanTransform3D;
use mmscenegraph_rust::node::traits::NodeCanTransformAndView3D;
use mmscenegraph_rust::node::traits::NodeCanViewScene;
use mmscenegraph_rust::node::traits::NodeHasId;
use mmscenegraph_rust::node::transform::TransformNode;
use mmscenegraph_rust::node::NodeId;
use mmscenegraph_rust::scene::graph::SceneGraph;

fn reproject_nodes(
    cam_tfm_matrix: Matrix44,
    cam_proj_matrix: Matrix44,
    tfm_matrix_list: Vec<Matrix44>,
) -> Vec<(Real, Real)> {
    let mut point_list = Vec::new();
    for tfm_matrix in tfm_matrix_list {
        let reproj_mat = reproject_as_normalised_coord(cam_tfm_matrix, cam_proj_matrix, tfm_matrix);
        let point = (reproj_mat[0], reproj_mat[1]);
        point_list.push(point);
    }
    point_list
}

#[test]
fn evaluate_scene() {
    println!("Set up Scene Graph");

    let mut sg = SceneGraph::new();
    assert_eq!(sg.num_transform_nodes(), 0);

    let rotate_order = RotateOrder::ZXY;

    let tfm_0 = sg.create_static_transform(
        (0.0, 42.0, 0.0),
        (15.0, 90.0, 0.0),
        (2.0, 3.0, 4.0),
        rotate_order,
    );
    let tfm_1 = sg.create_static_transform(
        (0.0, -10.0, 0.0),
        (0.0, 45.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let tfm_2 = sg.create_static_transform(
        (0.0, 100.0, 0.0),
        (0.0, 180.0, 0.0),
        (10.0, 10.0, 10.0),
        rotate_order,
    );
    let tfm_3 = sg.create_static_transform(
        (1.0, 0.0, -1.0),
        (0.0, -45.0, 0.0),
        (10.0, 10.0, 10.0),
        rotate_order,
    );
    let tfm_4 = sg.create_static_transform(
        (1.0, 0.0, -1.0),
        (0.0, 0.0, 22.0),
        (10.0, 10.0, 10.0),
        rotate_order,
    );

    sg.set_node_parent(tfm_0.get_id(), NodeId::Root);
    sg.set_node_parent(tfm_1.get_id(), tfm_0.get_id());
    sg.set_node_parent(tfm_2.get_id(), NodeId::Root);
    sg.set_node_parent(tfm_3.get_id(), tfm_1.get_id());
    sg.set_node_parent(tfm_4.get_id(), tfm_3.get_id());

    assert_eq!(sg.num_transform_nodes(), 5);

    println!("Transform 0: {:?}", tfm_0);
    println!("Transform 1: {:?}", tfm_1);
    println!("Transform 2: {:?}", tfm_2);
    println!("Transform 3: {:?}", tfm_3);
    println!("Transform 4: {:?}", tfm_4);
    println!("Scene Transforms count: {}", sg.num_transform_nodes());

    // Mark transform nodes as bundles.
    let rotate_order = RotateOrder::XYZ;
    let bnd_0 = sg.create_static_bundle(
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let bnd_1 = sg.create_static_bundle(
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let bnd_2 = sg.create_static_bundle(
        (0.0, 0.0, 1.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let bnd_3 = sg.create_static_bundle(
        (1.0, 1.0, 0.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let bnd_4 = sg.create_static_bundle(
        (1.0, 0.0, 1.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );

    sg.set_node_parent(bnd_0.get_id(), NodeId::Root);
    sg.set_node_parent(bnd_1.get_id(), tfm_1.get_id());
    sg.set_node_parent(bnd_2.get_id(), bnd_1.get_id());
    sg.set_node_parent(bnd_3.get_id(), tfm_3.get_id());
    sg.set_node_parent(bnd_4.get_id(), tfm_4.get_id());

    println!("Bundle 0: {:?}", bnd_0);
    println!("Bundle 1: {:?}", bnd_1);
    println!("Bundle 2: {:?}", bnd_2);
    println!("Bundle 3: {:?}", bnd_3);
    println!("Bundle 4: {:?}", bnd_4);
    println!("Scene Bundle count: {}", sg.num_bundle_nodes());

    // Create camera
    let cam_tfm = sg.create_static_transform(
        (0.0, 1000.0, 0.0),
        (45.0, 180.0, 45.0),
        (1.0, 1.0, 1.0),
        RotateOrder::XYZ,
    );

    let cam = sg.create_static_camera(
        (717.0, -514.0, 301.0),
        (9.0, 162.0, -56.0),
        (1.0, 1.0, 1.0),
        (36.0, 24.0),
        35.0,
        RotateOrder::ZXY,
    );
    sg.set_node_parent(cam.get_id(), cam_tfm.get_id());
    sg.set_node_parent(cam_tfm.get_id(), NodeId::Root);

    // let cam2 = sg.create_static_camera(
    //     (-99.0, 85.0, 150.0),
    //     (-10.0, -38.0, 0.0),
    //     (1.0, 1.0, 1.0),
    //     (36.0, 24.0),
    //     35.0,
    //     RotateOrder::ZXY,
    // );

    let cam_box = Box::new(cam) as Box<dyn NodeCanTransformAndView3D>;
    println!("Camera: {:?}", cam);
    println!("Scene Camera count: {}", sg.num_camera_nodes());

    // Add 'Markers' to be used and linked to Bundles
    let mkr_0 = sg.create_static_marker((-0.5, -0.5), 1.0);
    let mkr_1 = sg.create_static_marker((0.5, -0.5), 1.0);
    let mkr_2 = sg.create_static_marker((0.5, 0.5), 1.0);
    let mkr_3 = sg.create_static_marker((-0.5, 0.5), 1.0);
    let mkr_4 = sg.create_static_marker((0.0, 0.0), 1.0);

    let cam_node_id = cam.get_id();
    sg.link_marker_to_camera(mkr_0.get_id(), cam_node_id);
    sg.link_marker_to_camera(mkr_1.get_id(), cam_node_id);
    sg.link_marker_to_camera(mkr_2.get_id(), cam_node_id);
    sg.link_marker_to_camera(mkr_3.get_id(), cam_node_id);
    sg.link_marker_to_camera(mkr_4.get_id(), cam_node_id);

    sg.link_marker_to_bundle(mkr_0.get_id(), bnd_0.get_id());
    sg.link_marker_to_bundle(mkr_1.get_id(), bnd_1.get_id());
    sg.link_marker_to_bundle(mkr_2.get_id(), bnd_2.get_id());
    sg.link_marker_to_bundle(mkr_3.get_id(), bnd_3.get_id());
    sg.link_marker_to_bundle(mkr_4.get_id(), bnd_4.get_id());

    println!("Marker A: {:?}", mkr_0);
    println!("Marker B: {:?}", mkr_1);
    println!("Marker C: {:?}", mkr_2);
    println!("Marker D: {:?}", mkr_3);
    println!("Marker E: {:?}", mkr_4);
    println!("Scene Marker count: {}", sg.num_marker_nodes());

    let mut mkr_nodes = Vec::<Box<dyn NodeCanTransform2D>>::new();
    mkr_nodes.push(Box::new(mkr_0));
    mkr_nodes.push(Box::new(mkr_1));
    mkr_nodes.push(Box::new(mkr_2));
    mkr_nodes.push(Box::new(mkr_3));
    mkr_nodes.push(Box::new(mkr_4));

    let mut active_nodes = Vec::<Box<dyn NodeCanTransform3D>>::new();
    active_nodes.push(Box::new(bnd_0));
    active_nodes.push(Box::new(bnd_1));
    active_nodes.push(Box::new(bnd_2));
    active_nodes.push(Box::new(bnd_3));
    active_nodes.push(Box::new(bnd_4));
    active_nodes.push(Box::new(cam));

    // Calculate the bundle positions.
    let frame = 1001;
    let attr_data_block = sg.attr_data_block();

    let active_node_ids = active_nodes.iter().map(|x| x.get_id()).collect();
    let (sorted_node_indices, sorted_node_ids) = sg.sort_hierarchy(active_node_ids).unwrap();
    let sorted_nodes = sg.get_transformable_nodes(&sorted_node_ids).unwrap();
    let sorted_node_parent_indices = sg.get_parent_list(&sorted_node_indices);

    let mut world_matrix_list = Vec::new();
    let attr_data_block = sg.attr_data_block();
    compute_world_matrices(
        attr_data_block,
        &sorted_nodes,
        &sorted_node_parent_indices,
        frame,
        &mut world_matrix_list,
    );
    println!("World Matrix count: {}", world_matrix_list.len());

    let mut cam_tfm_matrix = Matrix44::identity();
    let mut bnd_world_matrix_list = Vec::new();
    let node_ids_and_matrix_iter = sorted_node_ids.iter().zip(world_matrix_list.iter());
    for (i, (node_id, world_matrix)) in (0..).zip(node_ids_and_matrix_iter) {
        match node_id {
            NodeId::Camera(index) => cam_tfm_matrix = *world_matrix,
            NodeId::Bundle(index) => bnd_world_matrix_list.push(*world_matrix),
            _ => (),
        }
    }
    println!("Bundle Matrix count: {}", bnd_world_matrix_list.len());
    println!("Camera Transform Matrix1: {}", cam_tfm_matrix);

    let cam_proj_matrix = compute_projection_matrix(attr_data_block, &cam_box, frame);
    println!("Camera Projection Matrix: {}", cam_proj_matrix);

    let point_list = reproject_nodes(cam_tfm_matrix, cam_proj_matrix, bnd_world_matrix_list);
    println!("Reprojected Points count: {}", point_list.len());
    println!("Reprojected Points: {:#?}", point_list);

    // TODO: Calculate deviation between Markers and Bundles.
    assert!(false);
}
