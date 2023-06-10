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
use mmscenegraph_rust::math::camera::FilmFit;
use mmscenegraph_rust::math::rotate::euler::RotateOrder;
use mmscenegraph_rust::node::traits::NodeCanTransformAndView3D;
use mmscenegraph_rust::node::traits::NodeHasId;
use mmscenegraph_rust::node::NodeId;
use mmscenegraph_rust::scene::bake::bake_scene_graph;
use mmscenegraph_rust::scene::evaluationobjects::EvaluationObjects;
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
        (0.0, 0.0),
        1.0,
        10000.0,
        1.0,
        RotateOrder::ZXY,
        FilmFit::Horizontal,
        2048,
        2048,
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
        (0.0, 0.0),
        1.0,
        10000.0,
        1.0,
        RotateOrder::ZXY,
        FilmFit::Horizontal,
        2048,
        2048,
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

    let mut eval_objects = EvaluationObjects::new();

    eval_objects.add_marker(mkr_0);
    eval_objects.add_marker(mkr_1);
    eval_objects.add_marker(mkr_2);
    eval_objects.add_marker(mkr_3);
    eval_objects.add_marker(mkr_4);

    eval_objects.add_bundle(bnd_0);
    eval_objects.add_bundle(bnd_1);
    eval_objects.add_bundle(bnd_2);
    eval_objects.add_bundle(bnd_3);
    eval_objects.add_bundle(bnd_4);

    eval_objects.add_camera(cam_0);
    eval_objects.add_camera(cam_1);

    let mut flat_scene = bake_scene_graph(&sg, &eval_objects);

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
    flat_scene.evaluate(&attrdb, &frame_list);

    let out_point_list = flat_scene.points();
    println!("2D Points (reprojected) count: {}", out_point_list.len());
    let points_iter = out_point_list.chunks_exact(2);
    for (i, point) in (0..).zip(points_iter) {
        println!("2D Point {}: pos: {:?}", i, point);
    }
}
