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
 * Command for calculating camera poses from known bundles positions.
 */

#include "MMCameraPoseFromPointsCmd.h"

// STL
#include <algorithm>
#include <array>
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

// MM Solver
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/sfm/camera_from_known_points.h"
#include "mmSolver/sfm/sfm_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

#define SET_VALUES_SHORT_FLAG "-sv"
#define SET_VALUES_LONG_FLAG "-setValues"

#define CAMERA_SHORT_FLAG "-c"
#define CAMERA_LONG_FLAG "-camera"

#define FRAME_SHORT_FLAG "-f"
#define FRAME_LONG_FLAG "-frame"

#define MARKER_SHORT_FLAG "-m"
#define MARKER_LONG_FLAG "-marker"

#define BUNDLE_SHORT_FLAG "-b"
#define BUNDLE_LONG_FLAG "-bundle"

namespace mmsolver {

MMCameraPoseFromPointsCmd::~MMCameraPoseFromPointsCmd() {}

void *MMCameraPoseFromPointsCmd::creator() {
    return new MMCameraPoseFromPointsCmd();
}

MString MMCameraPoseFromPointsCmd::cmdName() {
    return MString("mmCameraPoseFromPoints");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMCameraPoseFromPointsCmd::hasSyntax() const { return true; }

bool MMCameraPoseFromPointsCmd::isUndoable() const { return true; }

/*
 * Add flags to the command syntax
 */
MSyntax MMCameraPoseFromPointsCmd::newSyntax() {
    MStatus status = MStatus::kSuccess;

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    CHECK_MSTATUS(syntax.addFlag(SET_VALUES_SHORT_FLAG, SET_VALUES_LONG_FLAG,
                                 MSyntax::kBoolean));

    CHECK_MSTATUS(syntax.addFlag(CAMERA_SHORT_FLAG, CAMERA_LONG_FLAG,
                                 MSyntax::kSelectionItem));
    CHECK_MSTATUS(
        syntax.addFlag(FRAME_SHORT_FLAG, FRAME_LONG_FLAG, MSyntax::kUnsigned));
    CHECK_MSTATUS(syntax.makeFlagMultiUse(FRAME_SHORT_FLAG));

    CHECK_MSTATUS(syntax.addFlag(MARKER_SHORT_FLAG, MARKER_LONG_FLAG,
                                 MSyntax::kString, MSyntax::kString));
    CHECK_MSTATUS(syntax.makeFlagMultiUse(MARKER_SHORT_FLAG));

    CHECK_MSTATUS(
        syntax.addFlag(BUNDLE_SHORT_FLAG, BUNDLE_LONG_FLAG, MSyntax::kString));
    CHECK_MSTATUS(syntax.makeFlagMultiUse(BUNDLE_SHORT_FLAG));

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMCameraPoseFromPointsCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Reset saved data structures.
    m_marker_list.clear();
    m_frames.clear();
    m_times.clear();
    m_camera_rotate_order = MEulerRotation::kZXY;

    m_set_values = false;
    if (argData.isFlagSet(SET_VALUES_SHORT_FLAG)) {
        status =
            argData.getFlagArgument(SET_VALUES_SHORT_FLAG, 0, m_set_values);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // List of frames.
    const auto uiUnit = MTime::uiUnit();
    uint32_t numberOfFrameFlags = argData.numberOfFlagUses(FRAME_SHORT_FLAG);
    for (uint32_t i = 0; i < numberOfFrameFlags; ++i) {
        MArgList frameArgs;

        status = argData.getFlagArgumentList(FRAME_SHORT_FLAG, i, frameArgs);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        auto frame = 0;
        frame = frameArgs.asInt(0, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        auto frame_value = static_cast<double>(frame);
        auto time = MTime(frame_value, uiUnit);

        m_frames.push_back(frame);
        m_times.push_back(time);
    }
    MMSOLVER_MAYA_VRB("parse m_frames size: " << m_frames.size());

    MSelectionList camera_selection_list;
    argData.getFlagArgument(CAMERA_SHORT_FLAG, 0, camera_selection_list);
    status = ::mmsolver::sfm::parse_camera_argument(
        camera_selection_list, m_camera, m_camera_tx_attr, m_camera_ty_attr,
        m_camera_tz_attr, m_camera_rx_attr, m_camera_ry_attr, m_camera_rz_attr);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    m_camera->getRotateOrder(m_camera_rotate_order, m_times[0], timeEvalMode);

    // Parse objects as 2D Markers.
    uint32_t numberOfMarkerFlags = argData.numberOfFlagUses(MARKER_SHORT_FLAG);
    if (numberOfMarkerFlags > 6) {
        numberOfMarkerFlags = 6;
    }
    for (uint32_t i = 0; i < numberOfMarkerFlags; ++i) {
        MArgList markerArgs;
        MDagPath dagPath;
        MString markerName = "";
        MObject markerObject;
        status = argData.getFlagArgumentList(MARKER_SHORT_FLAG, i, markerArgs);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        markerName = markerArgs.asString(0, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsObject(markerName, markerObject);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsDagPath(markerName, dagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ObjectType objectType = computeObjectType(markerObject, dagPath);
        if (objectType != ObjectType::kMarker) {
            MMSOLVER_MAYA_ERR("Given marker node is not a Marker; "
                              << markerName.asChar());
            continue;
        }
        MMSOLVER_MAYA_VRB("Got markerName: " << markerName.asChar());

        MString bundleName = "";
        MObject bundleObject;
        bundleName = markerArgs.asString(1, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsObject(bundleName, bundleObject);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsDagPath(bundleName, dagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        objectType = computeObjectType(bundleObject, dagPath);
        if (objectType != ObjectType::kBundle) {
            MMSOLVER_MAYA_ERR("Given bundle node is not a Bundle; "
                              << bundleName.asChar());
            continue;
        }
        MMSOLVER_MAYA_VRB("Got bundleName: " << bundleName.asChar());

        MarkerPtr marker = MarkerPtr(new Marker());
        marker->setNodeName(markerName);
        marker->setCamera(m_camera);

        BundlePtr bundle = BundlePtr(new Bundle());
        bundle->setNodeName(bundleName);
        marker->setBundle(bundle);

        m_marker_list.push_back(marker);
    }
    MMSOLVER_MAYA_VRB("parse m_marker_list size: " << m_marker_list.size());

    return status;
}

MStatus MMCameraPoseFromPointsCmd::doIt(const MArgList &args) {
    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    // Read all the flag arguments.
    MStatus status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    // Command Outputs
    MDoubleArray outResult;
    // Intended to be used as a sentinal return value, informing the
    // user that something failed.
    const MDoubleArray emptyResult;

    const auto uiUnit = MTime::uiUnit();
    for (auto i = 0; i < m_times.size(); ++i) {
        MMSOLVER_MAYA_VRB("-------------------------------");
        auto frame = m_frames[i];
        auto time = m_times[i];
        MMSOLVER_MAYA_VRB("frame: " << frame);

        double focal_length_mm = 35.0;
        double sensor_width_mm = 36.0;
        double sensor_height_mm = 24.0;
        double focal_length_pix = 0.0;
        double ppx_pix = 0.0;
        double ppy_pix = 0.0;
        int32_t image_width = 2;
        int32_t image_height = 2;
        status = ::mmsolver::sfm::get_camera_values(
            time, m_camera, image_width, image_height, focal_length_mm,
            sensor_width_mm, sensor_height_mm);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        ::mmsolver::sfm::convert_camera_lens_mm_to_pixel_units(
            image_width, image_height, focal_length_mm, sensor_width_mm,
            focal_length_pix, ppx_pix, ppy_pix);

        MMSOLVER_MAYA_VRB("image (pixel): " << image_width << "x"
                                            << image_height);
        MMSOLVER_MAYA_VRB("sensor (mm): " << sensor_width_mm << "x"
                                          << sensor_height_mm);
        MMSOLVER_MAYA_VRB("focal (mm): " << focal_length_mm);
        MMSOLVER_MAYA_VRB("focal (pixel): " << focal_length_pix);
        MMSOLVER_MAYA_VRB("principal point (pixel): " << ppx_pix << "x"
                                                      << ppy_pix);

        MarkerPtrList marker_list;
        BundlePtrList bundle_list;
        std::vector<std::pair<double, double>> marker_coords;
        std::vector<std::tuple<double, double, double>> bundle_coords;
        std::shared_ptr<mmlens::LensModel> lensModel;

        for (auto j = 0; j < m_marker_list.size(); ++j) {
            auto marker = m_marker_list[j];
            auto marker_success = ::mmsolver::sfm::add_marker_at_frame(
                time, image_width, image_height, lensModel, marker,
                marker_coords);
            if (!marker_success) {
                continue;
            }

            auto bundle = marker->getBundle();
            auto bundle_success = ::mmsolver::sfm::add_bundle_at_frame(
                time, bundle, bundle_coords);
            if (bundle_success) {
                marker_list.push_back(marker);
                bundle_list.push_back(bundle);
            }
        }

        MTransformationMatrix pose_transform;
        auto pose_ok = ::mmsolver::sfm::compute_camera_pose_from_known_points(
            image_width, image_height, focal_length_pix, ppx_pix, ppy_pix,
            marker_coords, bundle_coords, pose_transform);
        if (!pose_ok) {
            MMSOLVER_MAYA_WRN("Compute Relative pose failed on frame "
                              << frame);
        }
        auto pose_matrix = pose_transform.asMatrix();

        if (m_set_values) {
            outResult.append(static_cast<double>(pose_ok));

            if (pose_ok) {
                auto world_euler_rotation = MEulerRotation::decompose(
                    pose_matrix, m_camera_rotate_order);
                auto rotate_x = world_euler_rotation.x * RADIANS_TO_DEGREES;
                auto rotate_y = world_euler_rotation.y * RADIANS_TO_DEGREES;
                auto rotate_z = world_euler_rotation.z * RADIANS_TO_DEGREES;

                const auto translate_x = pose_matrix(3, 0);
                const auto translate_y = pose_matrix(3, 1);
                const auto translate_z = pose_matrix(3, 2);

                m_camera_tx_attr.setValue(translate_x, time, m_dgmod,
                                          m_curveChange);
                m_camera_ty_attr.setValue(translate_y, time, m_dgmod,
                                          m_curveChange);
                m_camera_tz_attr.setValue(translate_z, time, m_dgmod,
                                          m_curveChange);

                m_camera_rx_attr.setValue(rotate_x, time, m_dgmod,
                                          m_curveChange);
                m_camera_ry_attr.setValue(rotate_y, time, m_dgmod,
                                          m_curveChange);
                m_camera_rz_attr.setValue(rotate_z, time, m_dgmod,
                                          m_curveChange);
            }
        } else {
            if (!pose_ok) {
                outResult.append(1.0);
                outResult.append(0.0);
                outResult.append(0.0);
                outResult.append(0.0);

                outResult.append(0.0);
                outResult.append(1.0);
                outResult.append(0.0);
                outResult.append(0.0);

                outResult.append(0.0);
                outResult.append(0.0);
                outResult.append(1.0);
                outResult.append(0.0);

                outResult.append(0.0);
                outResult.append(0.0);
                outResult.append(0.0);
                outResult.append(1.0);
            } else {
                outResult.append(pose_matrix(0, 0));
                outResult.append(pose_matrix(0, 1));
                outResult.append(pose_matrix(0, 2));
                outResult.append(pose_matrix(0, 3));
                outResult.append(pose_matrix(1, 0));
                outResult.append(pose_matrix(1, 1));
                outResult.append(pose_matrix(1, 2));
                outResult.append(pose_matrix(1, 3));
                outResult.append(pose_matrix(2, 0));
                outResult.append(pose_matrix(2, 1));
                outResult.append(pose_matrix(2, 2));
                outResult.append(pose_matrix(2, 3));
                outResult.append(pose_matrix(3, 0));
                outResult.append(pose_matrix(3, 1));
                outResult.append(pose_matrix(3, 2));
                outResult.append(pose_matrix(3, 3));
            }
        }
    }

    m_dgmod.doIt();

    MMCameraPoseFromPointsCmd::setResult(outResult);
    return status;
}

MStatus MMCameraPoseFromPointsCmd::redoIt() {
    MStatus status;
    m_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMCameraPoseFromPointsCmd::undoIt() {
    MStatus status;
    m_curveChange.undoIt();
    m_dgmod.undoIt();
    return status;
}

}  // namespace mmsolver
