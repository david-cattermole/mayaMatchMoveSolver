/*
 * Copyright (C) 2022 David Cattermole.
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
 * Calculate camera relative poses.
 */

// NOTE: The following (MSVC) warnings are disabled because of
// OpenMVG, and are mostly caused by Eigen. Annoyingly the warnings
// must be disabled at the top-level of the source file to fully get
// rid of the warnings - it's not possible to wrap these in
// 'push/pop'. Some warnings are also triggered in 'libmv', but not as
// many as 'OpenMVG'.

// Compiler Warning (level 3) C4267: conversion from 'size_t' to
// 'object', possible loss of data.
#pragma warning(disable : 4267)

// Compiler Warning (level 1) C4305: truncation from 'type1' to
// 'type2'.
#pragma warning(disable : 4305)

// Compiler Warning (level 4) C4127: conditional expression is
// constant
#pragma warning(disable : 4127)

// Compiler Warning (levels 3 and 4) C4244: 'conversion' conversion
// from 'type1' to 'type2', possible loss of data.
#pragma warning(disable : 4244)

// Compiler Warning (level 4) C4459: declaration of 'identifier' hides
// global declaration.
#pragma warning(disable : 4459)

// Compiler Warning (level 4) C4456: declaration of 'identifier' hides
// previous local declaration.
#pragma warning(disable : 4456)

// Compiler Warning (level 4) C4100: 'identifier' : unreferenced
// formal parameter.
#pragma warning(disable : 4100)

// Compiler Warning (level 3) C4018: 'token' : signed/unsigned
// mismatch.
#pragma warning(disable : 4018)

// Compiler Warning (level 4) C4714: function 'function' marked as
// __forceinline not inlined.
#pragma warning(disable : 4714)

// Compiler Warning (level 1) C4005: 'identifier' : macro
// redefinition.
#pragma warning(disable : 4005)

// Compiler Warning (level 4) C4702: unreachable code.
#pragma warning(disable : 4702)

#include "camera_relative_pose.h"

// STL
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <list>
#include <map>
#include <memory>
#include <string>
#include <thread>
#include <vector>

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <openMVG/numeric/numeric.h>

#include <openMVG/cameras/Camera_Intrinsics.hpp>
#include <openMVG/cameras/Camera_Pinhole.hpp>
#include <openMVG/features/feature.hpp>
#include <openMVG/features/feature_container.hpp>
#include <openMVG/geometry/pose3.hpp>
#include <openMVG/matching/indMatch.hpp>
#include <openMVG/matching/indMatchDecoratorXY.hpp>
#include <openMVG/matching/regions_matcher.hpp>
#include <openMVG/multiview/conditioning.hpp>
#include <openMVG/multiview/motion_from_essential.hpp>
#include <openMVG/multiview/solver_essential_eight_point.hpp>
#include <openMVG/multiview/solver_essential_kernel.hpp>
#include <openMVG/multiview/solver_fundamental_kernel.hpp>
#include <openMVG/multiview/triangulation.hpp>
#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/sfm/pipelines/sfm_robust_model_estimation.hpp>
#include <openMVG/sfm/sfm_data.hpp>
#include <openMVG/sfm/sfm_data_BA.hpp>
#include <openMVG/sfm/sfm_data_BA_ceres.hpp>
#include <openMVG/sfm/sfm_data_io.hpp>
#include <openMVG/types.hpp>

#endif  // MMSOLVER_USE_OPENMVG

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MEulerRotation.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MItSelectionList.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MTypes.h>

// Internal
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {
namespace sfm {

using MMMarker = Marker;
using MMCamera = Camera;

bool get_marker_coords(const MTime &time, MarkerPtr &mkr, double &x, double &y,
                       double &weight, bool &enable) {
    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;

    mkr->getPosXY(x, y, time, timeEvalMode);
    mkr->getEnable(enable, time, timeEvalMode);
    mkr->getWeight(weight, time, timeEvalMode);

    weight *= static_cast<double>(enable);
    return weight > 0;
}

// TODO: Replace this function wtih 'get_marker_coords'
bool get_marker_coord(const MTime time,
                      MMMarker &mkr, double &x, double &y, double &weight,
                      bool &enable) {
    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;

    mkr.getPosXY(x, y, time, timeEvalMode);
    mkr.getEnable(enable, time, timeEvalMode);
    mkr.getWeight(weight, time, timeEvalMode);

    weight *= static_cast<double>(enable);
    return weight > 0;
}

MStatus get_camera_values(const MTime &time, CameraPtr &cam, int &image_width,
                          int &image_height, double &focal_length_mm,
                          double &sensor_width_mm, double &sensor_height_mm) {
    MStatus status = MStatus::kSuccess;

    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;

    auto filmBackWidth_inch = cam->getFilmbackWidthValue(time, timeEvalMode);
    auto filmBackHeight_inch = cam->getFilmbackHeightValue(time, timeEvalMode);
    sensor_width_mm = filmBackWidth_inch * INCH_TO_MM;
    sensor_height_mm = filmBackHeight_inch * INCH_TO_MM;

    focal_length_mm = cam->getFocalLengthValue(time, timeEvalMode);

    image_width = static_cast<int>(sensor_width_mm * 1000.0);
    image_height = static_cast<int>(sensor_height_mm * 1000.0);

    return status;
}

bool get_camera_image_res(const uint32_t frame_num, const MTime::Unit &uiUnit,
                          MMCamera &cam, int &image_width, int &image_height) {
    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    auto frame = static_cast<double>(frame_num);
    MTime time = MTime(frame, uiUnit);

    auto filmBackWidth = cam.getFilmbackWidthValue(time, timeEvalMode);
    auto filmBackHeight = cam.getFilmbackHeightValue(time, timeEvalMode);
    image_width = static_cast<int>(filmBackWidth * 10000.0);
    image_height = static_cast<int>(filmBackHeight * 10000.0);
    return true;
}

MStatus parseCameraSelectionList(
    const MSelectionList &selection_list, const MTime &time, CameraPtr &camera,
    Attr &camera_tx_attr, Attr &camera_ty_attr, Attr &camera_tz_attr,
    Attr &camera_rx_attr, Attr &camera_ry_attr, Attr &camera_rz_attr,
    int32_t &image_width, int32_t &image_height, double &focal_length_mm,
    double &sensor_width_mm, double &sensor_height_mm) {
    MMSOLVER_INFO("parseCameraSelectionList1");
    MStatus status = MStatus::kSuccess;

    MDagPath nodeDagPath;
    MObject node_obj;

    if (selection_list.length() > 0) {
        status = selection_list.getDagPath(0, nodeDagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = selection_list.getDependNode(0, node_obj);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        MString transform_node_name = nodeDagPath.fullPathName();
        MMSOLVER_INFO("Camera name: " << transform_node_name.asChar());

        auto object_type = computeObjectType(node_obj, nodeDagPath);
        if (object_type == ObjectType::kCamera) {
            MMSOLVER_INFO("parseCameraSelectionList2");
            status = nodeDagPath.extendToShapeDirectlyBelow(0);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MString shape_node_name = nodeDagPath.fullPathName();

            MMSOLVER_INFO("parseCameraSelectionList3");
            camera = CameraPtr(new Camera());
            camera->setTransformNodeName(transform_node_name);
            camera->setShapeNodeName(shape_node_name);

            MMSOLVER_INFO("parseCameraSelectionList4");
            camera_tx_attr.setNodeName(transform_node_name);
            camera_ty_attr.setNodeName(transform_node_name);
            camera_tz_attr.setNodeName(transform_node_name);
            camera_rx_attr.setNodeName(transform_node_name);
            camera_ry_attr.setNodeName(transform_node_name);
            camera_rz_attr.setNodeName(transform_node_name);

            MMSOLVER_INFO("parseCameraSelectionList5");
            camera_tx_attr.setAttrName(MString("translateX"));
            camera_ty_attr.setAttrName(MString("translateY"));
            camera_tz_attr.setAttrName(MString("translateZ"));
            camera_rx_attr.setAttrName(MString("rotateX"));
            camera_ry_attr.setAttrName(MString("rotateY"));
            camera_rz_attr.setAttrName(MString("rotateZ"));

            MMSOLVER_INFO("parseCameraSelectionList6");
            status = get_camera_values(time, camera, image_width, image_height,
                                       focal_length_mm, sensor_width_mm,
                                       sensor_height_mm);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        } else {
            MMSOLVER_ERR("Given node is not a valid camera: "
                         << transform_node_name.asChar());
            status = MS::kFailure;
            return status;
        }
    }

    MMSOLVER_INFO("parseCameraSelectionList7");
    return status;
}

MStatus addMarkerBundles(
    const MTime &time_a, const MTime &time_b, const int32_t image_width_a,
    const int32_t image_height_a, const int32_t image_width_b,
    const int32_t image_height_b, MarkerPtr &marker_a, MarkerPtr &marker_b,
    BundlePtr &bundle, BundlePtrList &bundle_list, MarkerPtrList &marker_list_a,
    MarkerPtrList &marker_list_b,
    std::vector<std::pair<double, double>> &marker_coords_a,
    std::vector<std::pair<double, double>> &marker_coords_b) {
    MMSOLVER_INFO("addMarkerBundle1");
    MStatus status = MStatus::kSuccess;

    double x_a = 0.0;
    double x_b = 0.0;
    double y_a = 0.0;
    double y_b = 0.0;
    bool enable_a = true;
    bool enable_b = true;
    double weight_a = 1.0;
    double weight_b = 1.0;

    auto success_a =
        get_marker_coords(time_a, marker_a, x_a, y_a, weight_a, enable_a);
    MMSOLVER_INFO("addMarkerBundle2");
    auto success_b =
        get_marker_coords(time_b, marker_b, x_b, y_b, weight_b, enable_b);
    MMSOLVER_INFO("addMarkerBundle3");
    if (success_a && success_b) {
        MMSOLVER_INFO("addMarkerBundle4");
        double xx_a = (x_a + 0.5) * static_cast<double>(image_width_a);
        double yy_a = (y_a + 0.5) * static_cast<double>(image_height_a);
        double xx_b = (x_b + 0.5) * static_cast<double>(image_width_b);
        double yy_b = (y_b + 0.5) * static_cast<double>(image_height_b);
        MMSOLVER_INFO("x_a : " << x_a << " y_a : " << y_a);
        MMSOLVER_INFO("xx_a: " << xx_a << " yy_a: " << yy_a);
        MMSOLVER_INFO("x_b : " << x_b << " y_b : " << y_b);
        MMSOLVER_INFO("xx_b: " << xx_b << " yy_b: " << yy_b);
        auto xy_a = std::pair<double, double>{xx_a, yy_a};
        auto xy_b = std::pair<double, double>{xx_b, yy_b};
        MMSOLVER_INFO("addMarkerBundle5");
        marker_coords_a.push_back(xy_a);
        marker_coords_b.push_back(xy_b);

        MMSOLVER_INFO("addMarkerBundle6");
        marker_list_a.push_back(marker_a);
        marker_list_b.push_back(marker_b);
        bundle_list.push_back(bundle);
    }

    MMSOLVER_INFO("addMarkerBundle7");
    return status;
}

}  // namespace sfm
}  // namespace mmsolver
