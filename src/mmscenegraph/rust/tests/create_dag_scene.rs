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


use mmscenegraph_rust::attr::datablock::AttrDataBlock;
use mmscenegraph_rust::math::rotate::euler::RotateOrder;
use mmscenegraph_rust::node::traits::NodeCanTransform2D;
use mmscenegraph_rust::node::traits::NodeCanTransform3D;
use mmscenegraph_rust::node::traits::NodeCanTransformAndView3D;
use mmscenegraph_rust::node::traits::NodeHasId;
use mmscenegraph_rust::node::NodeId;
use mmscenegraph_rust::scene::bake::bake_scene_graph;
use mmscenegraph_rust::scene::graph::SceneGraph;
use mmscenegraph_rust::scene::helper::create_static_bundle;
use mmscenegraph_rust::scene::helper::create_static_camera;
use mmscenegraph_rust::scene::helper::create_static_marker;
use mmscenegraph_rust::scene::helper::create_static_transform;

#[test]
fn evaluate_scene() {
    println!("Set up Scene Graph");

    let mut sg = SceneGraph::new();
    let mut attrdb = AttrDataBlock::new();
    assert_eq!(sg.num_transform_nodes(), 0);

    let rotate_order = RotateOrder::ZXY;

    let tfm_0 = create_static_transform(
        &mut sg,
        &mut attrdb,
        (0.0, 42.0, 0.0),
        (15.0, 90.0, 0.0),
        (2.0, 3.0, 4.0),
        rotate_order,
    );
    let tfm_1 = create_static_transform(
        &mut sg,
        &mut attrdb,
        (0.0, -10.0, 0.0),
        (0.0, 45.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let tfm_2 = create_static_transform(
        &mut sg,
        &mut attrdb,
        (0.0, 100.0, 0.0),
        (0.0, 180.0, 0.0),
        (10.0, 10.0, 10.0),
        rotate_order,
    );
    let tfm_3 = create_static_transform(
        &mut sg,
        &mut attrdb,
        (1.0, 0.0, -1.0),
        (0.0, -45.0, 0.0),
        (10.0, 10.0, 10.0),
        rotate_order,
    );
    let tfm_4 = create_static_transform(
        &mut sg,
        &mut attrdb,
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
    let bnd_0 = create_static_bundle(
        &mut sg,
        &mut attrdb,
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let bnd_1 = create_static_bundle(
        &mut sg,
        &mut attrdb,
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let bnd_2 = create_static_bundle(
        &mut sg,
        &mut attrdb,
        (0.0, 0.0, 1.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let bnd_3 = create_static_bundle(
        &mut sg,
        &mut attrdb,
        (1.0, 1.0, 0.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        rotate_order,
    );
    let bnd_4 = create_static_bundle(
        &mut sg,
        &mut attrdb,
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
    let cam_0_tfm = create_static_transform(
        &mut sg,
        &mut attrdb,
        (0.0, 1000.0, 0.0),
        (45.0, 180.0, 45.0),
        (1.0, 1.0, 1.0),
        RotateOrder::XYZ,
    );
    let cam_0 = create_static_camera(
        &mut sg,
        &mut attrdb,
        (717.0, -514.0, 301.0),
        (9.0, 162.0, -56.0),
        (1.0, 1.0, 1.0),
        (36.0, 24.0),
        35.0,
        RotateOrder::ZXY,
    );
    sg.set_node_parent(cam_0.get_id(), cam_0_tfm.get_id());
    sg.set_node_parent(cam_0_tfm.get_id(), NodeId::Root);

    let cam_1 = create_static_camera(
        &mut sg,
        &mut attrdb,
        (-99.0, 85.0, 150.0),
        (-10.0, -38.0, 0.0),
        (1.0, 1.0, 1.0),
        (36.0, 24.0),
        40.0,
        RotateOrder::ZXY,
    );
    println!("Camera 1: {:?}", cam_0);
    println!("Camera 2: {:?}", cam_1);
    println!("Scene Camera count: {}", sg.num_camera_nodes());

    let mut cam_nodes = Vec::<Box<dyn NodeCanTransformAndView3D>>::new();
    let cam_0_box = Box::new(cam_0) as Box<dyn NodeCanTransformAndView3D>;
    let cam_1_box = Box::new(cam_1) as Box<dyn NodeCanTransformAndView3D>;
    cam_nodes.push(cam_0_box);
    cam_nodes.push(cam_1_box);

    // Add 'Markers' to be used and linked to Bundles
    let mkr_0 = create_static_marker(&mut sg, &mut attrdb, (-0.5, -0.5), 1.0);
    let mkr_1 = create_static_marker(&mut sg, &mut attrdb, (0.5, -0.5), 1.0);
    let mkr_2 = create_static_marker(&mut sg, &mut attrdb, (0.5, 0.5), 1.0);
    let mkr_3 = create_static_marker(&mut sg, &mut attrdb, (-0.5, 0.5), 1.0);
    let mkr_4 = create_static_marker(&mut sg, &mut attrdb, (0.0, 0.0), 1.0);

    let cam_0_node_id = cam_0.get_id();
    let cam_1_node_id = cam_1.get_id();
    sg.link_marker_to_camera(mkr_0.get_id(), cam_0_node_id);
    sg.link_marker_to_camera(mkr_1.get_id(), cam_0_node_id);
    sg.link_marker_to_camera(mkr_2.get_id(), cam_0_node_id);
    sg.link_marker_to_camera(mkr_3.get_id(), cam_1_node_id);
    sg.link_marker_to_camera(mkr_4.get_id(), cam_1_node_id);

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

    let mut bnd_nodes = Vec::<Box<dyn NodeCanTransform3D>>::new();
    bnd_nodes.push(Box::new(bnd_0));
    bnd_nodes.push(Box::new(bnd_1));
    bnd_nodes.push(Box::new(bnd_2));
    bnd_nodes.push(Box::new(bnd_3));
    bnd_nodes.push(Box::new(bnd_4));

    // Note: It doesn't matter if we add non-bundle nodes to this
    // list, they will be filtered out correctly in the
    // FlatScene.evalutate() call.
    bnd_nodes.push(Box::new(cam_0));
    bnd_nodes.push(Box::new(cam_1));

    let flat_scene = bake_scene_graph(&sg, &bnd_nodes, &cam_nodes, &mkr_nodes);

    let mut frame_list = Vec::new();
    frame_list.push(1001);
    frame_list.push(1002);
    frame_list.push(1003);
    frame_list.push(1004);
    frame_list.push(1005);

    // Evaluate the FlatScene:
    // - Calculate all the local and world-space matrices for the objects.
    // - Calculate the camera projection matrices.
    // - Calculate deviation between Markers and Bundles.
    let mut out_tfm_world_matrix_list = Vec::new();
    let mut out_bnd_world_matrix_list = Vec::new();
    let mut out_cam_world_matrix_list = Vec::new();
    let mut out_point_list = Vec::new();
    let mut out_deviation_list = Vec::new();
    flat_scene.evaluate(
        &attrdb,
        &frame_list,
        &mut out_tfm_world_matrix_list,
        &mut out_bnd_world_matrix_list,
        &mut out_cam_world_matrix_list,
        &mut out_point_list,
        &mut out_deviation_list,
    );

    println!("2D Points (reprojected) count: {}", out_point_list.len());
    println!("Deviation count: {}", out_deviation_list.len());
    for (i, (point, dev)) in (0..).zip(out_point_list.iter().zip(out_deviation_list)) {
        println!("2D Point {}: pos: {:?} dev: {:?}", i, point, dev);
    }

    assert!(false);
}
