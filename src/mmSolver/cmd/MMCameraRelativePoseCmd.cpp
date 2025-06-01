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
 * Command for calculating camera relative poses.

import maya.cmds

nodes = maya.cmds.ls('cam_tfm', long=True) or []
nodes += maya.cmds.ls('Track_*_MKR', long=True) or []

maya.cmds.loadPlugin('mmSolver', quiet=True)

# Possible flags for this tool.
maya.cmds.mmCameraRelativePose(
    cameraA='cameraA',
    cameraB='cameraB',
    frameA=21,
    frameB=29,
    markerBundle=[
        ('markerA1', 'markerB1', 'bundle1'),
        ('markerA2', 'markerB2', 'bundle2'),
        ('markerA3', 'markerB3', 'bundle3'),
        ('markerA4', 'markerB4', 'bundle4'),
        ('markerA5', 'markerB5', 'bundle5'),
        ('markerA6', 'markerB6', 'bundle6'),
    ],
)

#########################################################################

import pprint
import maya.cmds
import mmSolver.api as mmapi

# nodes = maya.cmds.ls('cam_tfm', long=True) or []
mkr_nodes = maya.cmds.ls('Track_*_MKR', long=True) or []

mkr_list = []
mkr_bnd_list = []
for mkr_node in mkr_nodes:
    mkr = mmapi.Marker(node=mkr_node)
    mkr_list.append(mkr)

    bnd = mkr.get_bundle()
    if bnd:
        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()
        mkr_bnd = [mkr_node, mkr_node, bnd_node]
        mkr_bnd_list.append(mkr_bnd)

# pprint.pprint(mkr_bnd_list)

maya.cmds.loadPlugin('mmSolver', quiet=True)
maya.cmds.mmCameraRelativePose(
    frameA=22,
    frameB=29,
    cameraA='cam_tfm',
    cameraB='cam_tfm',
    markerBundle=mkr_bnd_list
)

 */

#include "MMCameraRelativePoseCmd.h"

// STL
#include <algorithm>
#include <array>
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

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_lens_model_utils.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_list.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/sfm/camera_relative_pose.h"
#include "mmSolver/sfm/sfm_utils.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

#define SET_VALUES_SHORT_FLAG "-sv"
#define SET_VALUES_LONG_FLAG "-setValues"

#define CAMERA_A_SHORT_FLAG "-ca"
#define CAMERA_A_LONG_FLAG "-cameraA"

#define CAMERA_B_SHORT_FLAG "-cb"
#define CAMERA_B_LONG_FLAG "-cameraB"

#define FRAME_A_SHORT_FLAG "-fa"
#define FRAME_A_LONG_FLAG "-frameA"

#define FRAME_B_SHORT_FLAG "-fb"
#define FRAME_B_LONG_FLAG "-frameB"

#define USE_CAMERA_TRANSFORM_SHORT_FLAG "-ct"
#define USE_CAMERA_TRANSFORM_LONG_FLAG "-useCameraTransform"

#define MARKER_BUNDLE_SHORT_FLAG "-mb"
#define MARKER_BUNDLE_LONG_FLAG "-markerBundle"

// NOTE: The Bundle Positions are expected to be in the same
// world-space as cameraA, so when looking through cameraA, the bundle
// positions should align/match to the related marker (with some
// deviation).
#define BUNDLE_POSITION_SHORT_FLAG "-bp"
#define BUNDLE_POSITION_LONG_FLAG "-bundlePosition"

namespace mmsolver {

MMCameraRelativePoseCmd::~MMCameraRelativePoseCmd() {}

void *MMCameraRelativePoseCmd::creator() {
    return new MMCameraRelativePoseCmd();
}

MString MMCameraRelativePoseCmd::cmdName() {
    return MString("mmCameraRelativePose");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMCameraRelativePoseCmd::hasSyntax() const { return true; }

bool MMCameraRelativePoseCmd::isUndoable() const { return true; }

/*
 * Add flags to the command syntax
 */
MSyntax MMCameraRelativePoseCmd::newSyntax() {
    MStatus status = MStatus::kSuccess;

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    CHECK_MSTATUS(syntax.addFlag(SET_VALUES_SHORT_FLAG, SET_VALUES_LONG_FLAG,
                                 MSyntax::kBoolean));

    CHECK_MSTATUS(syntax.addFlag(CAMERA_A_SHORT_FLAG, CAMERA_A_LONG_FLAG,
                                 MSyntax::kSelectionItem));
    CHECK_MSTATUS(syntax.addFlag(CAMERA_B_SHORT_FLAG, CAMERA_B_LONG_FLAG,
                                 MSyntax::kSelectionItem));

    CHECK_MSTATUS(
        syntax.addFlag(FRAME_A_SHORT_FLAG, FRAME_A_LONG_FLAG, MSyntax::kLong));
    CHECK_MSTATUS(
        syntax.addFlag(FRAME_B_SHORT_FLAG, FRAME_B_LONG_FLAG, MSyntax::kLong));

    CHECK_MSTATUS(syntax.addFlag(USE_CAMERA_TRANSFORM_SHORT_FLAG,
                                 USE_CAMERA_TRANSFORM_LONG_FLAG,
                                 MSyntax::kBoolean));

    CHECK_MSTATUS(syntax.addFlag(MARKER_BUNDLE_SHORT_FLAG,
                                 MARKER_BUNDLE_LONG_FLAG, MSyntax::kString,
                                 MSyntax::kString, MSyntax::kString));
    CHECK_MSTATUS(syntax.makeFlagMultiUse(MARKER_BUNDLE_SHORT_FLAG));

    CHECK_MSTATUS(syntax.addFlag(BUNDLE_POSITION_SHORT_FLAG,
                                 BUNDLE_POSITION_LONG_FLAG, MSyntax::kDouble,
                                 MSyntax::kDouble, MSyntax::kDouble));
    CHECK_MSTATUS(syntax.makeFlagMultiUse(BUNDLE_POSITION_SHORT_FLAG));

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMCameraRelativePoseCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Reset saved data structures.
    m_marker_list_a.clear();
    m_marker_list_b.clear();
    m_bundle_list.clear();
    m_bundle_pos_list.clear();
    m_marker_coords_a.clear();
    m_marker_coords_b.clear();
    m_image_width_a = 1;
    m_image_height_a = 1;
    m_image_width_b = 1;
    m_image_height_b = 1;
    m_focal_length_mm_a = 35.0;
    m_focal_length_mm_b = 35.0;
    m_sensor_width_mm_a = 36.0;
    m_sensor_width_mm_b = 36.0;
    m_sensor_height_mm_a = 24.0;
    m_sensor_height_mm_b = 24.0;

    m_frame_a = 1;
    if (argData.isFlagSet(FRAME_A_SHORT_FLAG)) {
        int value = 0;
        status = argData.getFlagArgument(FRAME_A_SHORT_FLAG, 0, value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        m_frame_a = static_cast<FrameNumber>(value);
    }

    m_frame_b = 1;
    if (argData.isFlagSet(FRAME_B_SHORT_FLAG)) {
        int value = 0;
        status = argData.getFlagArgument(FRAME_B_SHORT_FLAG, 0, value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        m_frame_b = static_cast<FrameNumber>(value);
    }

    m_use_camera_transform = false;
    m_camera_transform_matrix = MMatrix();
    if (argData.isFlagSet(USE_CAMERA_TRANSFORM_SHORT_FLAG)) {
        status = argData.getFlagArgument(USE_CAMERA_TRANSFORM_SHORT_FLAG, 0,
                                         m_use_camera_transform);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    m_set_values = false;
    if (argData.isFlagSet(SET_VALUES_SHORT_FLAG)) {
        status =
            argData.getFlagArgument(SET_VALUES_SHORT_FLAG, 0, m_set_values);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    const auto uiUnit = MTime::uiUnit();
    const auto frame_value_a = static_cast<double>(m_frame_a);
    const auto frame_value_b = static_cast<double>(m_frame_b);
    m_time_a = MTime(frame_value_a, uiUnit);
    m_time_b = MTime(frame_value_b, uiUnit);

    MSelectionList camera_selection_list_a;
    argData.getFlagArgument(CAMERA_A_SHORT_FLAG, 0, camera_selection_list_a);
    status = ::mmsolver::sfm::parseCameraSelectionList(
        camera_selection_list_a, m_time_a, m_camera_a, m_camera_tx_attr_a,
        m_camera_ty_attr_a, m_camera_tz_attr_a, m_camera_rx_attr_a,
        m_camera_ry_attr_a, m_camera_rz_attr_a, m_image_width_a,
        m_image_height_a, m_focal_length_mm_a, m_sensor_width_mm_a,
        m_sensor_height_mm_a);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MSelectionList camera_selection_list_b;
    argData.getFlagArgument(CAMERA_B_SHORT_FLAG, 0, camera_selection_list_b);
    status = ::mmsolver::sfm::parseCameraSelectionList(
        camera_selection_list_b, m_time_b, m_camera_b, m_camera_tx_attr_b,
        m_camera_ty_attr_b, m_camera_tz_attr_b, m_camera_rx_attr_b,
        m_camera_ry_attr_b, m_camera_rz_attr_b, m_image_width_b,
        m_image_height_b, m_focal_length_mm_b, m_sensor_width_mm_b,
        m_sensor_height_mm_b);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    {
        const auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
        m_camera_a->getRotateOrder(m_camera_rotate_order_a, m_time_a,
                                   timeEvalMode);
        m_camera_b->getRotateOrder(m_camera_rotate_order_b, m_time_b,
                                   timeEvalMode);
    }

    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "image A: "
        << m_image_width_a << "x" << m_image_height_a);
    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "image B: "
        << m_image_width_b << "x" << m_image_height_b);
    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "sensor (mm) A: "
        << m_sensor_width_mm_a << "x" << m_sensor_height_mm_a);
    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "sensor (mm) B: "
        << m_sensor_width_mm_b << "x" << m_sensor_height_mm_b);
    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "focal (mm) A: "
        << m_focal_length_mm_a);
    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "focal (mm) B: "
        << m_focal_length_mm_b);

    // The camera A matrix that will be used to offset the relative
    // pose result.
    if (m_use_camera_transform) {
        // The 'matrix' attribute is local space, not world
        // space. This is intentional so that all calculations are
        // relative to this matrix. Therefore the camera and bundles
        // can be grouped to a 'hero transform' and have all solved
        // values be relative to this hero transform. The hero
        // transform might be a line up frame, so that the camera pose
        // is always solved relative to this line-up frame.
        auto camera_matrix_attr = Attr();
        auto transform_node_name = m_camera_a->getTransformNodeName();
        camera_matrix_attr.setNodeName(transform_node_name);
        camera_matrix_attr.setAttrName("matrix");

        auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
        status = camera_matrix_attr.getValue(m_camera_transform_matrix,
                                             m_time_a, timeEvalMode);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    const uint32_t numberOfBundlePositionFlags =
        argData.numberOfFlagUses(BUNDLE_POSITION_SHORT_FLAG);
    const uint32_t numberOfMarkerBundleFlags =
        argData.numberOfFlagUses(MARKER_BUNDLE_SHORT_FLAG);
    const bool hasBundlePositionFlags = numberOfBundlePositionFlags > 0;
    if (hasBundlePositionFlags &&
        (numberOfMarkerBundleFlags != numberOfBundlePositionFlags)) {
        MMSOLVER_MAYA_ERR(
            "mmCameraRelativePose: "
            "Bundle Position argument list must have "
            "same number of arguments "
            "as marker bundles("
            << MARKER_BUNDLE_SHORT_FLAG << "/" << MARKER_BUNDLE_LONG_FLAG
            << "); " << BUNDLE_POSITION_LONG_FLAG << "="
            << numberOfBundlePositionFlags << " | " << MARKER_BUNDLE_LONG_FLAG
            << "=" << numberOfMarkerBundleFlags);
        return MS::kFailure;
    }

    m_marker_list_a.reserve(numberOfMarkerBundleFlags);
    m_marker_list_b.reserve(numberOfMarkerBundleFlags);
    m_bundle_list.reserve(numberOfMarkerBundleFlags);
    m_bundle_pos_list.reserve(numberOfBundlePositionFlags * 3);
    m_marker_coords_a.reserve(numberOfMarkerBundleFlags);
    m_marker_coords_b.reserve(numberOfMarkerBundleFlags);

    // Temporary variables, for querying lens models for markers.
    //
    // Defined outside loop to re-use memory, and avoid fragmentation.
    std::shared_ptr<mmlens::LensModel> lensModel_a;
    std::shared_ptr<mmlens::LensModel> lensModel_b;
    MarkerList markerList;
    CameraPtrList cameraList;
    AttrList attrList;  // Empty, but needed for 'constructLensModelList'.
    FrameList frameList;
    std::vector<std::shared_ptr<mmlens::LensModel>> markerFrameToLensModelList;
    std::vector<std::shared_ptr<mmlens::LensModel>> attrFrameToLensModelList;
    std::vector<std::shared_ptr<mmlens::LensModel>> lensModelList;

    // Temporary variables
    MDagPath dagPath;
    MString markerNameA;
    MString markerNameB;
    MString bundleName;
    MObject markerObject;
    MObject bundleObject;

    markerList.reserve(2);
    cameraList.reserve(2);
    frameList.reserve(2);

    // Parse objects into Camera intrinsics and Tracking Markers.
    for (uint32_t i = 0; i < numberOfMarkerBundleFlags; ++i) {
        // Reset reused variables.
        markerNameA.clear();
        markerNameB.clear();
        bundleName.clear();
        lensModel_a.reset();
        lensModel_b.reset();

        MArgList markerBundleArgs;
        status = argData.getFlagArgumentList(MARKER_BUNDLE_SHORT_FLAG, i,
                                             markerBundleArgs);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (markerBundleArgs.length() != 3) {
            MMSOLVER_MAYA_ERR(
                "mmCameraRelativePose: "
                "Marker Bundle argument list must have 3 arguments; "
                << "\"markerA\", \"markerB\",  \"bundle\".");
            continue;
        }

        // Bundles with "NaN" values are considered unknown.
        double bundlePosition_x = NAN;
        double bundlePosition_y = NAN;
        double bundlePosition_z = NAN;
        if (hasBundlePositionFlags) {
            MArgList bundlePositionArgs;
            status = argData.getFlagArgumentList(BUNDLE_POSITION_SHORT_FLAG, i,
                                                 bundlePositionArgs);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            if (bundlePositionArgs.length() != 3) {
                MMSOLVER_MAYA_ERR(
                    "mmCameraRelativePose: "
                    "Bundle Position argument list must have 3 arguments; "
                    "(pos_x, pos_y, pos_z)");
                continue;
            }

            bundlePosition_x = bundlePositionArgs.asDouble(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            bundlePosition_y = bundlePositionArgs.asDouble(1, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            bundlePosition_z = bundlePositionArgs.asDouble(2, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }

        ObjectType objectType = ObjectType::kUnknown;

        markerNameA = markerBundleArgs.asString(0, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsObject(markerNameA, markerObject);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsDagPath(markerNameA, dagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        objectType = computeObjectType(markerObject, dagPath);
        if (objectType != ObjectType::kMarker) {
            MMSOLVER_MAYA_ERR(
                "mmCameraRelativePose: "
                "Given marker node is not a Marker; "
                << markerNameA.asChar());
            continue;
        }
        MMSOLVER_MAYA_VRB(
            "mmCameraRelativePose: "
            "Got markerNameA: "
            << markerNameA.asChar());

        markerNameB = markerBundleArgs.asString(1, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsObject(markerNameB, markerObject);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsDagPath(markerNameB, dagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        objectType = computeObjectType(markerObject, dagPath);
        if (objectType != ObjectType::kMarker) {
            MMSOLVER_MAYA_ERR(
                "mmCameraRelativePose: "
                "Given marker node is not a Marker; "
                << markerNameB.asChar());
            continue;
        }
        MMSOLVER_MAYA_VRB(
            "mmCameraRelativePose: "
            "Got markerNameB: "
            << markerNameB.asChar());

        bundleName = markerBundleArgs.asString(2, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsObject(bundleName, bundleObject);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsDagPath(bundleName, dagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        objectType = computeObjectType(bundleObject, dagPath);
        if (objectType != ObjectType::kBundle) {
            MMSOLVER_MAYA_ERR(
                "mmCameraRelativePose: "
                "Given bundle node is not a Bundle; "
                << bundleName.asChar());
            continue;
        }
        MMSOLVER_MAYA_VRB(
            "mmCameraRelativePose: "
            "Got bundleName: "
            << bundleName.asChar());

        MMSOLVER_MAYA_VRB(
            "mmCameraRelativePose: "
            "Got bundlePosition: ("
            << bundlePosition_x << ", " << bundlePosition_y << ", "
            << bundlePosition_z << ")");

        BundlePtr bundle = BundlePtr(new Bundle());
        bundle->setNodeName(bundleName);

        MarkerPtr marker_a = MarkerPtr(new Marker());
        marker_a->setNodeName(markerNameA);
        marker_a->setBundle(bundle);
        marker_a->setCamera(m_camera_a);

        MarkerPtr marker_b = MarkerPtr(new Marker());
        marker_b->setNodeName(markerNameB);
        marker_b->setBundle(bundle);
        marker_b->setCamera(m_camera_b);

        // Get lens models for each marker, a and b.
        {
            markerList.clear();
            markerList.push_back(marker_a, /*enabled=*/true);
            markerList.push_back(marker_b, /*enabled=*/true);

            cameraList.clear();
            cameraList.push_back(m_camera_a);
            cameraList.push_back(m_camera_b);

            frameList.clear();
            frameList.push_back(m_frame_a, /*enabled=*/true);
            frameList.push_back(m_frame_b, /*enabled=*/true);

            markerFrameToLensModelList.clear();
            attrFrameToLensModelList.clear();
            lensModelList.clear();
            status = mmsolver::constructLensModelList(
                cameraList, markerList, attrList, frameList,
                markerFrameToLensModelList, attrFrameToLensModelList,
                lensModelList);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            lensModel_a = markerFrameToLensModelList[0];
            lensModel_b = markerFrameToLensModelList[1];
        }

        const auto success = ::mmsolver::sfm::add_marker_pair_at_frame(
            m_time_a, m_time_b, m_image_width_a, m_image_width_b,
            m_image_height_a, m_image_height_b, lensModel_a, lensModel_b,
            marker_a, marker_b, m_marker_coords_a, m_marker_coords_b);
        if (success) {
            m_marker_list_a.push_back(marker_a, /*enabled=*/true);
            m_marker_list_b.push_back(marker_b, /*enabled=*/true);
            m_bundle_list.push_back(bundle);
            m_bundle_pos_list.push_back(bundlePosition_x);
            m_bundle_pos_list.push_back(bundlePosition_y);
            m_bundle_pos_list.push_back(bundlePosition_z);
        }
    }

    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "parse m_marker_list_a size: "
        << m_marker_list_a.size());
    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "parse m_marker_list_b size: "
        << m_marker_list_b.size());
    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "parse m_bundle_list size: "
        << m_bundle_list.size());
    MMSOLVER_ASSERT(m_marker_list_a.size() == m_marker_list_b.size(),
                    "Must have matching marker counts.");
    MMSOLVER_ASSERT(m_marker_list_a.size() == m_bundle_list.size(),
                    "Must have matching bundle counts.");

    return status;
}

MStatus MMCameraRelativePoseCmd::doIt(const MArgList &args) {
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

    // Essential geometry filtering of putative matches
    double focal_length_pix_a = 0.0;
    double focal_length_pix_b = 0.0;
    double ppx_pix_a = 0.0;
    double ppx_pix_b = 0.0;
    double ppy_pix_a = 0.0;
    double ppy_pix_b = 0.0;
    ::mmsolver::sfm::convert_camera_lens_mm_to_pixel_units(
        m_image_width_a, m_image_height_a, m_focal_length_mm_a,
        m_sensor_width_mm_a, focal_length_pix_a, ppx_pix_a, ppy_pix_a);
    ::mmsolver::sfm::convert_camera_lens_mm_to_pixel_units(
        m_image_width_b, m_image_height_b, m_focal_length_mm_b,
        m_sensor_width_mm_b, focal_length_pix_b, ppx_pix_b, ppy_pix_b);

    openMVG::sfm::RelativePose_Info pose_info;
    auto relative_pose_ok = ::mmsolver::sfm::compute_relative_pose(
        m_image_width_a, m_image_width_b, m_image_height_a, m_image_height_b,
        focal_length_pix_a, focal_length_pix_b, ppx_pix_a, ppx_pix_b, ppy_pix_a,
        ppy_pix_b, m_marker_coords_a, m_marker_coords_b, m_marker_list_a,
        m_marker_list_b, pose_info);
    if (!relative_pose_ok) {
        MMSOLVER_MAYA_ERR(
            "mmCameraRelativePose: "
            "Compute Relative pose failed using "
            << m_marker_list_a.size() << " markers; "
            << "frame A=" << m_frame_a << " frame B=" << m_frame_b << ".");
        MMCameraRelativePoseCmd::setResult(emptyResult);
        return status;
    }

    openMVG::sfm::SfM_Data scene;
    auto sfm_data_ok = ::mmsolver::sfm::construct_two_camera_sfm_data_scene(
        m_image_width_a, m_image_width_b, m_image_height_a, m_image_height_b,
        focal_length_pix_a, focal_length_pix_b, ppx_pix_a, ppx_pix_b, ppy_pix_a,
        ppy_pix_b, pose_info, scene);
    if (!sfm_data_ok) {
        MMSOLVER_MAYA_ERR(
            "mmCameraRelativePose: "
            "Failed to construct two camera SfM scene.");
        MMCameraRelativePoseCmd::setResult(emptyResult);
        return status;
    }

    // Triangulate and check valid points. Invalid points that do not
    // work are discarded (removed from the list of inliers).
    //
    // Init structure by inlier triangulation
    double camera_translation_scale = 1.0;
    auto triangulate_ok = ::mmsolver::sfm::triangulate_relative_pose(
        m_marker_coords_a, m_marker_coords_b, pose_info.vec_inliers,
        m_marker_list_a, m_marker_list_b, m_bundle_list, m_bundle_pos_list,
        m_camera_transform_matrix, scene, camera_translation_scale);
    if (!triangulate_ok) {
        MMSOLVER_MAYA_ERR(
            "mmCameraRelativePose: "
            "Triangulate relative pose points failed.");
        MMCameraRelativePoseCmd::setResult(emptyResult);
        return status;
    }
    MMSOLVER_MAYA_VRB(
        "mmCameraRelativePose: "
        "camera_translation_scale: "
        << camera_translation_scale);

    // Refine the scene.
#if 0
    // The Ceres bundle adjustment sometimes produced bundle positions
    // very far from camera, which caused the solve to fail miserably.
    auto adjust_ok = ::mmsolver::sfm::bundle_adjustment(scene);
    if (!adjust_ok) {
        MMSOLVER_MAYA_ERR("mmCameraRelativePose: "
                          "Bundle Adjustment failed.");
        status = MS::kFailure;
        MMCameraRelativePoseCmd::setResult(emptyResult);
        return status;
    }
#endif

    // Convert the sfm_data back to Maya data and set Camera and
    // Bundles.
    //
    // TODO: Add the new camera pose relative to existing frameA
    // camera position.
    auto views = scene.GetViews();
    auto poses = scene.GetPoses();
    auto intrinsics = scene.GetIntrinsics();
    for (auto it : views) {
        const auto key = it.first;
        const auto view = *it.second;
        const auto pose_id = view.id_pose;
        MMSOLVER_MAYA_VRB(
            "mmCameraRelativePose: "
            "view: "
            << key << "=" << pose_id);

        // Per-camera values
        auto attr_tx = m_camera_tx_attr_b;
        auto attr_ty = m_camera_ty_attr_b;
        auto attr_tz = m_camera_tz_attr_b;
        auto attr_rx = m_camera_rx_attr_b;
        auto attr_ry = m_camera_ry_attr_b;
        auto attr_rz = m_camera_rz_attr_b;
        auto rotate_order = m_camera_rotate_order_b;
        auto value_time = m_time_b;
        if (pose_id == 0) {
            value_time = m_time_a;
            attr_tx = m_camera_tx_attr_a;
            attr_ty = m_camera_ty_attr_a;
            attr_tz = m_camera_tz_attr_a;
            attr_rx = m_camera_rx_attr_a;
            attr_ry = m_camera_ry_attr_a;
            attr_rz = m_camera_rz_attr_a;
            rotate_order = m_camera_rotate_order_a;
        }

        const auto pose = scene.GetPoseOrDie(&view);
        const auto transform =
            ::mmsolver::sfm::convert_pose_to_maya_transform_matrix(
                pose, camera_translation_scale);

        auto transform_matrix = transform.asMatrix();
        transform_matrix = transform_matrix * m_camera_transform_matrix;

        outResult.append(transform_matrix(0, 0));
        outResult.append(transform_matrix(0, 1));
        outResult.append(transform_matrix(0, 2));
        outResult.append(transform_matrix(0, 3));
        outResult.append(transform_matrix(1, 0));
        outResult.append(transform_matrix(1, 1));
        outResult.append(transform_matrix(1, 2));
        outResult.append(transform_matrix(1, 3));
        outResult.append(transform_matrix(2, 0));
        outResult.append(transform_matrix(2, 1));
        outResult.append(transform_matrix(2, 2));
        outResult.append(transform_matrix(2, 3));
        outResult.append(transform_matrix(3, 0));
        outResult.append(transform_matrix(3, 1));
        outResult.append(transform_matrix(3, 2));
        outResult.append(transform_matrix(3, 3));

        if (m_set_values) {
            const auto world_euler_rotation =
                MEulerRotation::decompose(transform_matrix, rotate_order);
            const auto rotate_x = world_euler_rotation.x * RADIANS_TO_DEGREES;
            const auto rotate_y = world_euler_rotation.y * RADIANS_TO_DEGREES;
            const auto rotate_z = world_euler_rotation.z * RADIANS_TO_DEGREES;

            const auto translate_x = transform_matrix(3, 0);
            const auto translate_y = transform_matrix(3, 1);
            const auto translate_z = transform_matrix(3, 2);

            attr_tx.setValue(translate_x, value_time, m_dgmod, m_curveChange);
            attr_ty.setValue(translate_y, value_time, m_dgmod, m_curveChange);
            attr_tz.setValue(translate_z, value_time, m_dgmod, m_curveChange);

            attr_rx.setValue(rotate_x, value_time, m_dgmod, m_curveChange);
            attr_ry.setValue(rotate_y, value_time, m_dgmod, m_curveChange);
            attr_rz.setValue(rotate_z, value_time, m_dgmod, m_curveChange);
        }
    }

    auto attr_tx = Attr();
    auto attr_ty = Attr();
    auto attr_tz = Attr();

    const MMatrix inverse_camera_transform_matrix =
        m_camera_transform_matrix.inverse();

    auto landmarks = scene.GetLandmarks();
    auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    auto output_bundle_index = 0;
    for (auto it : landmarks) {
        auto inlier_idx = it.first;
        auto landmark = it.second;
        auto pos = landmark.X;
        const double tx = pos[0];
        const double ty = pos[1];
        // Fixes the Camera +Z/-Z issue with Maya compared to OpenMVG.
        const double tz = -pos[2];
        MPoint maya_translate(tx, ty, tz);

        const auto inlier_idx_x = (inlier_idx * 3) + 0;
        const auto inlier_idx_y = (inlier_idx * 3) + 1;
        const auto inlier_idx_z = (inlier_idx * 3) + 2;
        const double known_bnd_pos_x = m_bundle_pos_list[inlier_idx_x];
        const double known_bnd_pos_y = m_bundle_pos_list[inlier_idx_y];
        const double known_bnd_pos_z = m_bundle_pos_list[inlier_idx_z];
        const bool is_known_bundle_pos =
            (!std::isnan(known_bnd_pos_x) && !std::isnan(known_bnd_pos_y) &&
             !std::isnan(known_bnd_pos_z));
        if (is_known_bundle_pos) {
            // The known bundle position is expected to already
            // contain the 'm_camera_transform_matrix' baked in.
            maya_translate.x = known_bnd_pos_x;
            maya_translate.y = known_bnd_pos_y;
            maya_translate.z = known_bnd_pos_z;
            maya_translate *= inverse_camera_transform_matrix;
        }

        if ((output_bundle_index >= m_bundle_list.size()) ||
            (inlier_idx >= m_bundle_list.size())) {
            MMSOLVER_MAYA_ERR(
                "mmCameraRelativePose: "
                "Bundle index \""
                << output_bundle_index
                << "\" is outside bounds, camera pose failed.");
            MMCameraRelativePoseCmd::setResult(emptyResult);
            return status;
        }

        auto bnd = m_bundle_list[inlier_idx];
        auto bnd_name = bnd->getNodeName();
        MMSOLVER_MAYA_VRB(
            "mmCameraRelativePose: "
            "landmark bnd: "
            << bnd_name.asChar() << " | inlier_idx=" << inlier_idx
            << " x=" << maya_translate.x << " y=" << maya_translate.y
            << " z=" << maya_translate.z << " | known=" << is_known_bundle_pos);

        maya_translate *= m_camera_transform_matrix;
        outResult.append(static_cast<double>(output_bundle_index));
        outResult.append(maya_translate.x);
        outResult.append(maya_translate.y);
        outResult.append(maya_translate.z);

        if (m_set_values) {
            attr_tx.setNodeName(bnd_name);
            attr_ty.setNodeName(bnd_name);
            attr_tz.setNodeName(bnd_name);

            attr_tx.setAttrName(MString("translateX"));
            attr_ty.setAttrName(MString("translateY"));
            attr_tz.setAttrName(MString("translateZ"));

            attr_tx.setValue(maya_translate.x, m_dgmod, m_curveChange);
            attr_ty.setValue(maya_translate.y, m_dgmod, m_curveChange);
            attr_tz.setValue(maya_translate.z, m_dgmod, m_curveChange);
        }

        ++output_bundle_index;
    }

    m_dgmod.doIt();

    MMCameraRelativePoseCmd::setResult(outResult);
    return status;
}

MStatus MMCameraRelativePoseCmd::redoIt() {
    MStatus status;
    m_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMCameraRelativePoseCmd::undoIt() {
    MStatus status;
    m_curveChange.undoIt();
    m_dgmod.undoIt();
    return status;
}

}  // namespace mmsolver
