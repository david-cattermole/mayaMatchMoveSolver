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
use mmscenegraph_rust::node::traits::NodeHasId;
use mmscenegraph_rust::scene::bake::bake_scene_graph;
use mmscenegraph_rust::scene::evaluationobjects::EvaluationObjects;
use mmscenegraph_rust::scene::graph::SceneGraph;
use mmscenegraph_rust::scene::helper::create_static_bundle;
use mmscenegraph_rust::scene::helper::create_static_camera;
use mmscenegraph_rust::scene::helper::create_static_marker;

#[test]
fn evaluate_scene() {
    println!("Set up Scene Graph");

    let mut sg = SceneGraph::new();
    let mut attrdb = AttrDataBlock::new();
    assert_eq!(sg.num_transform_nodes(), 0);

    let bnd = create_static_bundle(
        &mut sg,
        &mut attrdb,
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        RotateOrder::XYZ,
    );
    let cam = create_static_camera(
        &mut sg,
        &mut attrdb,
        (-99.0, 85.0, 150.0),
        (-10.0, -38.0, 0.0),
        (1.0, 1.0, 1.0),
        (36.0, 24.0),
        40.0,
        RotateOrder::ZXY,
    );

    let mkr = create_static_marker(&mut sg, &mut attrdb, (0.0, 0.0), 1.0);
    sg.link_marker_to_camera(mkr.get_id(), cam.get_id());
    sg.link_marker_to_bundle(mkr.get_id(), bnd.get_id());

    println!("Bundle: {:?}", bnd);
    println!("Camera: {:?}", cam);
    println!("Marker: {:?}", mkr);
    println!("Scene Bundle count: {}", sg.num_bundle_nodes());
    println!("Scene Camera count: {}", sg.num_camera_nodes());
    println!("Scene Marker count: {}", sg.num_marker_nodes());

    let mut eval_objects = EvaluationObjects::new();
    eval_objects.add_marker(mkr);
    eval_objects.add_bundle(bnd);
    eval_objects.add_camera(cam);

    let mut flat_scene = bake_scene_graph(&sg, &eval_objects);

    let mut frame_list = Vec::new();
    frame_list.push(1001);

    flat_scene.evaluate(&attrdb, &frame_list);

    let out_point_list = flat_scene.points();
    let out_marker_list = flat_scene.markers();
    let out_deviation_list = flat_scene.deviations();
    println!("2D Points (reprojected) count: {}", out_point_list.len());
    println!("2D Markers count: {}", out_marker_list.len());
    println!("Deviation count: {}", out_deviation_list.len());
    let points_iter = out_point_list.chunks_exact(2);
    let marker_iter = out_marker_list.chunks_exact(2);
    let dev_iter = out_deviation_list.chunks_exact(2);
    let point_dev_iter = points_iter.zip(marker_iter.zip(dev_iter));
    for (i, (point, (mkr, dev))) in (0..).zip(point_dev_iter) {
        println!(
            "2D Point {}: mkr: {:?} reprojected: {:?} dev: {:?}",
            i, mkr, point, dev
        );
    }
}
