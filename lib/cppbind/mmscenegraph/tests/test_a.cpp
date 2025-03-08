/*
 * Copyright (C) 2020, 2021 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 */

#include "test_a.h"

// MM Solver Libs
#include <mmscenegraph/mmscenegraph.h>
#include <mmsolverlibs/assert.h>

// STL
#include <iostream>

namespace mmsg = mmscenegraph;

int test_a() {
    // Hold the attribute data.
    auto attrdb = mmsg::AttrDataBlock();

    // Holds the nodes and structure of the graph.
    auto sg = mmsg::SceneGraph();

    // Common attribute values, not to be edited.
    auto zero_attr = attrdb.create_attr_static(0.0);
    auto one_attr = attrdb.create_attr_static(1.0);

    // Root transform.
    auto root_translate_attrs = mmsg::Translate3DAttrIds{
        zero_attr,
        zero_attr,
        zero_attr,
    };
    auto root_rotate_attrs = mmsg::Rotate3DAttrIds{
        zero_attr,
        zero_attr,
        zero_attr,
    };
    auto root_scale_attrs = mmsg::Scale3DAttrIds{
        one_attr,
        one_attr,
        one_attr,
    };
    auto root_rotate_order = mmsg::RotateOrder::kXYZ;
    auto root_node =
        sg.create_transform_node(root_translate_attrs, root_rotate_attrs,
                                 root_scale_attrs, root_rotate_order);

    // Bundle to be reprojected
    mmsg::Real px = -0.5;
    mmsg::Real py = 2.7;
    mmsg::Real pz = 0.0;
    auto px_attr = attrdb.create_attr_static(px);
    auto py_attr = attrdb.create_attr_static(py);
    auto pz_attr = attrdb.create_attr_static(pz);
    auto bnd_translate_attrs = mmsg::Translate3DAttrIds{
        px_attr,
        py_attr,
        pz_attr,
    };
    auto bnd_rotate_attrs = mmsg::Rotate3DAttrIds{
        zero_attr,
        zero_attr,
        zero_attr,
    };
    auto bnd_scale_attrs = mmsg::Scale3DAttrIds{
        one_attr,
        one_attr,
        one_attr,
    };
    auto bnd_rotate_order = mmsg::RotateOrder::kXYZ;
    auto bnd_node = sg.create_bundle_node(bnd_translate_attrs, bnd_rotate_attrs,
                                          bnd_scale_attrs, bnd_rotate_order);

    // Camera Values
    mmsg::Real tx = -2.0;
    mmsg::Real ty = 2.0;
    mmsg::Real tz = 5.0;
    mmsg::Real rx = 10.0;
    mmsg::Real ry = -10.0;
    mmsg::Real rz = -10.0;
    mmsg::Real focal_length = 35.0f;
    mmsg::Real sensor_width = 36.0f;
    mmsg::Real sensor_height = 24.0f;
    int32_t image_width = 3600;
    int32_t image_height = 2400;
    auto cam_film_fit = mmsg::FilmFit::kHorizontal;
    auto cam_tx_attr = attrdb.create_attr_static(tx);
    auto cam_ty_attr = attrdb.create_attr_static(ty);
    auto cam_tz_attr = attrdb.create_attr_static(tz);
    auto cam_rx_attr = attrdb.create_attr_static(rx);
    auto cam_ry_attr = attrdb.create_attr_static(ry);
    auto cam_rz_attr = attrdb.create_attr_static(rz);
    auto cam_sensor_width_attr = attrdb.create_attr_static(sensor_width);
    auto cam_sensor_height_attr = attrdb.create_attr_static(sensor_height);
    auto cam_focal_length_attr = attrdb.create_attr_static(focal_length);
    auto cam_lens_offset_x_attr = attrdb.create_attr_static(0.0);
    auto cam_lens_offset_y_attr = attrdb.create_attr_static(0.0);
    auto cam_near_clip_plane_attr = attrdb.create_attr_static(0.1);
    auto cam_far_clip_plane_attr = attrdb.create_attr_static(10000.0);
    auto cam_camera_scale_attr = attrdb.create_attr_static(1.0);
    auto cam_translate_attrs = mmsg::Translate3DAttrIds{
        cam_tx_attr,
        cam_ty_attr,
        cam_tz_attr,
    };
    auto cam_rotate_attrs = mmsg::Rotate3DAttrIds{
        cam_rx_attr,
        cam_ry_attr,
        cam_rz_attr,
    };
    auto cam_scale_attrs = mmsg::Scale3DAttrIds{
        one_attr,
        one_attr,
        one_attr,
    };
    // Beware that initializing this struct (and others like it) will
    // automatically initialize the attributes not given to the
    // default value of the type. For 'CameraAttrIds' this means that
    // if the last attribute is removed from the initalisation then it
    // will default to an 'AttrId::AnimDense(0)' value which will at
    // least cause incorrect results and at worse it will segfault the
    // program.
    auto cam_attrs =
        mmsg::CameraAttrIds{cam_sensor_width_attr,   cam_sensor_height_attr,
                            cam_focal_length_attr,   cam_lens_offset_x_attr,
                            cam_lens_offset_y_attr,  cam_near_clip_plane_attr,
                            cam_far_clip_plane_attr, cam_camera_scale_attr};
    auto cam_rotate_order = mmsg::RotateOrder::kZXY;
    auto cam_node = sg.create_camera_node(
        cam_translate_attrs, cam_rotate_attrs, cam_scale_attrs, cam_attrs,
        cam_rotate_order, cam_film_fit, image_width, image_height);

    // Marker to be reprojected
    mmsg::Real mx = 0.0;
    mmsg::Real my = 0.0;
    mmsg::Real weight = 1.0;
    auto mx_attr = attrdb.create_attr_static(mx);
    auto my_attr = attrdb.create_attr_static(my);
    auto weight_attr = attrdb.create_attr_static(weight);
    auto mkr_attrs = mmsg::MarkerAttrIds{
        mx_attr,
        my_attr,
        weight_attr,
    };
    auto mkr_node = sg.create_marker_node(mkr_attrs);

    // Print number of nodes in the scene graph.
    std::cout << "SceneGraph num_transform_nodes: " << sg.num_transform_nodes()
              << '\n';
    std::cout << "SceneGraph num_bundle_nodes: " << sg.num_bundle_nodes()
              << '\n';
    std::cout << "SceneGraph num_camera_nodes: " << sg.num_camera_nodes()
              << '\n';
    std::cout << "SceneGraph num_marker_nodes: " << sg.num_marker_nodes()
              << '\n';

    // Create Marker, Bundle and Camera relationships.
    sg.link_marker_to_camera(mkr_node.id, cam_node.id);
    sg.link_marker_to_bundle(mkr_node.id, bnd_node.id);

    // Set node hierarchy.
    sg.set_node_parent(cam_node.id, root_node.id);
    sg.set_node_parent(bnd_node.id, root_node.id);

    // Bake down SceneGraph into FlatScene for fast evaluation.
    auto eval_objects = mmsg::EvaluationObjects();
    eval_objects.add_bundle(bnd_node);
    eval_objects.add_camera(cam_node);
    eval_objects.add_marker(mkr_node);

    // Print number of nodes in the scene graph.
    std::cout << "EvaluationObjects num_bundles: " << eval_objects.num_bundles()
              << '\n';
    std::cout << "EvaluationObjects num_cameras: " << eval_objects.num_cameras()
              << '\n';
    std::cout << "EvaluationObjects num_markers: " << eval_objects.num_markers()
              << '\n';

    auto flat_scene = mmsg::bake_scene_graph(sg, eval_objects);
    std::cout << "FlatScene BEFORE num_points: " << flat_scene.num_points()
              << '\n';
    std::cout << "FlatScene BEFORE num_markers: " << flat_scene.num_markers()
              << '\n';

    auto frames = std::vector<mmsg::FrameValue>();
    frames.push_back(1);

    // Evaluate
    flat_scene.evaluate(attrdb, frames);
    std::cout << "FlatScene AFTER num_points: " << flat_scene.num_points()
              << '\n';
    std::cout << "FlatScene AFTER num_markers: " << flat_scene.num_markers()
              << '\n';
    auto num_points = flat_scene.num_points();
    MMSOLVER_CORE_ASSERT(
        num_points == flat_scene.num_markers(),
        "Point count flat scene representation must be the same to "
        "be logically consistent.");

    auto out_marker_list = flat_scene.markers();
    auto out_point_list = flat_scene.points();
    MMSOLVER_CORE_ASSERT(out_point_list.size() == out_marker_list.size(),
                         "Points and Markers need to be the same size.");
    for (uint32_t i = 0; i < num_points; ++i) {
        auto index = i * 2;
        auto point_x = out_point_list[index + 0];
        auto point_y = out_point_list[index + 1];
        auto marker_x = out_marker_list[index + 0];
        auto marker_y = out_marker_list[index + 1];
        std::cout << "point: " << point_x << ", " << point_y
                  << " marker: " << marker_x << ", " << marker_y << '\n';
    }

    return 0;
}
