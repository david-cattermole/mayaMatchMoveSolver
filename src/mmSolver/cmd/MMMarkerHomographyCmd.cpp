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
 * Command for calculating a 2D homography matrix.

import maya.cmds

nodes = maya.cmds.ls('cam_tfm', long=True) or []
nodes += maya.cmds.ls('Track_*_MKR', long=True) or []

maya.cmds.loadPlugin('mmSolver', quiet=True)

# Possible flags for this tool.
maya.cmds.mmMarkerHomography(
    cameraA='cameraA',
    cameraB='cameraB',
    frameA=21,
    frameB=29,
    marker=[
        ('markerA1', 'markerB1'),
        ('markerA2', 'markerB2'),
        ('markerA3', 'markerB3'),
        ('markerA4', 'markerB4'),
        ('markerA5', 'markerB5'),
        ('markerA6', 'markerB6'),
    ],
)

#########################################################################

import pprint
import maya.cmds
import mmSolver.api as mmapi

# nodes = maya.cmds.ls('cam_tfm', long=True) or []
mkr_nodes = maya.cmds.ls('Track_*_MKR', long=True) or []

mkr_pair_list = []
for mkr_node in mkr_nodes:
    mkr = mmapi.Marker(node=mkr_node)
    mkr_node = mkr.get_node()
    mkr_bnd = [mkr_node, mkr_node]
    mkr_pair_list.append(mkr_bnd)

# pprint.pprint(mkr_pair_list)

maya.cmds.loadPlugin('mmSolver', quiet=True)
maya.cmds.mmMarkerHomography(
    frameA=22,
    frameB=29,
    cameraA='cam_tfm',
    cameraB='cam_tfm',
    marker=mkr_pair_list
)

 */

#include "MMMarkerHomographyCmd.h"

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
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_lens_model_utils.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/sfm/homography.h"
#include "mmSolver/sfm/sfm_utils.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

#define CAMERA_A_SHORT_FLAG "-ca"
#define CAMERA_A_LONG_FLAG "-cameraA"

#define CAMERA_B_SHORT_FLAG "-cb"
#define CAMERA_B_LONG_FLAG "-cameraB"

#define FRAME_A_SHORT_FLAG "-fa"
#define FRAME_A_LONG_FLAG "-frameA"

#define FRAME_B_SHORT_FLAG "-fb"
#define FRAME_B_LONG_FLAG "-frameB"

#define MARKER_PAIR_SHORT_FLAG "-mp"
#define MARKER_PAIR_LONG_FLAG "-markerPair"

namespace mmsolver {

MMMarkerHomographyCmd::~MMMarkerHomographyCmd() {}

void *MMMarkerHomographyCmd::creator() { return new MMMarkerHomographyCmd(); }

MString MMMarkerHomographyCmd::cmdName() {
    return MString("mmMarkerHomography");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMMarkerHomographyCmd::hasSyntax() const { return true; }

bool MMMarkerHomographyCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMMarkerHomographyCmd::newSyntax() {
    MStatus status = MStatus::kSuccess;

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    CHECK_MSTATUS(syntax.addFlag(CAMERA_A_SHORT_FLAG, CAMERA_A_LONG_FLAG,
                                 MSyntax::kSelectionItem));
    CHECK_MSTATUS(syntax.addFlag(CAMERA_B_SHORT_FLAG, CAMERA_B_LONG_FLAG,
                                 MSyntax::kSelectionItem));

    CHECK_MSTATUS(syntax.addFlag(FRAME_A_SHORT_FLAG, FRAME_A_LONG_FLAG,
                                 MSyntax::kUnsigned));
    CHECK_MSTATUS(syntax.addFlag(FRAME_B_SHORT_FLAG, FRAME_B_LONG_FLAG,
                                 MSyntax::kUnsigned));

    CHECK_MSTATUS(syntax.addFlag(MARKER_PAIR_SHORT_FLAG, MARKER_PAIR_LONG_FLAG,
                                 MSyntax::kString, MSyntax::kString));
    CHECK_MSTATUS(syntax.makeFlagMultiUse(MARKER_PAIR_SHORT_FLAG));

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMMarkerHomographyCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Reset saved data structures.
    m_marker_coords_a.clear();
    m_marker_coords_b.clear();
    m_image_width_a = 1;
    m_image_height_a = 1;
    m_image_width_b = 1;
    m_image_height_b = 1;

    m_frame_a = 1;
    if (argData.isFlagSet(FRAME_A_SHORT_FLAG)) {
        status = argData.getFlagArgument(FRAME_A_SHORT_FLAG, 0, m_frame_a);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    m_frame_b = 1;
    if (argData.isFlagSet(FRAME_B_SHORT_FLAG)) {
        status = argData.getFlagArgument(FRAME_B_SHORT_FLAG, 0, m_frame_b);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto uiUnit = MTime::uiUnit();
    auto frame_value_a = static_cast<double>(m_frame_a);
    auto frame_value_b = static_cast<double>(m_frame_b);
    m_time_a = MTime(frame_value_a, uiUnit);
    m_time_b = MTime(frame_value_b, uiUnit);

    MSelectionList camera_selection_list_a;
    argData.getFlagArgument(CAMERA_A_SHORT_FLAG, 0, camera_selection_list_a);
    status = ::mmsolver::sfm::parse_camera_argument(
        camera_selection_list_a, m_camera_a, m_camera_tx_attr_a,
        m_camera_ty_attr_a, m_camera_tz_attr_a, m_camera_rx_attr_a,
        m_camera_ry_attr_a, m_camera_rz_attr_a);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MSelectionList camera_selection_list_b;
    argData.getFlagArgument(CAMERA_B_SHORT_FLAG, 0, camera_selection_list_b);
    status = ::mmsolver::sfm::parse_camera_argument(
        camera_selection_list_b, m_camera_b, m_camera_tx_attr_b,
        m_camera_ty_attr_b, m_camera_tz_attr_b, m_camera_rx_attr_b,
        m_camera_ry_attr_b, m_camera_rz_attr_b);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    auto image_res_a_ok = ::mmsolver::sfm::get_camera_image_res(
        m_frame_a, uiUnit, *m_camera_a, m_image_width_a, m_image_height_a);
    if (!image_res_a_ok) {
        status = MS::kFailure;
        return status;
    }

    auto image_res_b_ok = ::mmsolver::sfm::get_camera_image_res(
        m_frame_b, uiUnit, *m_camera_b, m_image_width_b, m_image_height_b);
    if (!image_res_b_ok) {
        status = MS::kFailure;
        return status;
    }

    MMSOLVER_MAYA_VRB("image A: " << m_image_width_a << "x"
                                  << m_image_height_a);
    MMSOLVER_MAYA_VRB("image B: " << m_image_width_b << "x"
                                  << m_image_height_b);

    // Parse objects into Camera intrinsics and Tracking Markers.
    uint32_t numberOfMarkerFlags =
        argData.numberOfFlagUses(MARKER_PAIR_SHORT_FLAG);
    for (uint32_t i = 0; i < numberOfMarkerFlags; ++i) {
        MArgList markerArgs;
        ObjectType objectType = ObjectType::kUnknown;
        MDagPath dagPath;
        MString markerNameA = "";
        MString markerNameB = "";
        MObject markerObject;
        status =
            argData.getFlagArgumentList(MARKER_PAIR_SHORT_FLAG, i, markerArgs);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        if (markerArgs.length() != 2) {
            MMSOLVER_MAYA_ERR("Marker argument list must have 2 arguments; "
                              << "\"markerA\", \"markerB\".");
            continue;
        }

        markerNameA = markerArgs.asString(0, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsObject(markerNameA, markerObject);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsDagPath(markerNameA, dagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        objectType = computeObjectType(markerObject, dagPath);
        if (objectType != ObjectType::kMarker) {
            MMSOLVER_MAYA_ERR("Given marker node is not a Marker; "
                              << markerNameA.asChar());
            continue;
        }
        MMSOLVER_MAYA_VRB("Got markerNameA: " << markerNameA.asChar());

        markerNameB = markerArgs.asString(1, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsObject(markerNameB, markerObject);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsDagPath(markerNameB, dagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        objectType = computeObjectType(markerObject, dagPath);
        if (objectType != ObjectType::kMarker) {
            MMSOLVER_MAYA_ERR("Given marker node is not a Marker; "
                              << markerNameB.asChar());
            continue;
        }
        MMSOLVER_MAYA_VRB("Got markerNameB: " << markerNameB.asChar());

        MarkerPtr marker_a = MarkerPtr(new Marker());
        marker_a->setNodeName(markerNameA);
        marker_a->setCamera(m_camera_a);

        MarkerPtr marker_b = MarkerPtr(new Marker());
        marker_b->setNodeName(markerNameB);
        marker_b->setCamera(m_camera_b);

        std::shared_ptr<mmlens::LensModel> lensModel_a;
        std::shared_ptr<mmlens::LensModel> lensModel_b;
        {
            MarkerList markerList;
            markerList.push_back(marker_a, /*enabled=*/true);
            markerList.push_back(marker_b, /*enabled=*/true);

            CameraPtrList cameraList;
            cameraList.push_back(m_camera_a);
            cameraList.push_back(m_camera_b);

            AttrList attrList;

            FrameList frameList;
            frameList.reserve(2);
            frameList.push_back(m_frame_a, true);
            frameList.push_back(m_frame_b, true);

            std::vector<std::shared_ptr<mmlens::LensModel>>
                markerFrameToLensModelList;
            std::vector<std::shared_ptr<mmlens::LensModel>>
                attrFrameToLensModelList;
            std::vector<std::shared_ptr<mmlens::LensModel>> lensModelList;

            status = mmsolver::constructLensModelList(
                cameraList, markerList, attrList, frameList,
                markerFrameToLensModelList, attrFrameToLensModelList,
                lensModelList);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            lensModel_a = markerFrameToLensModelList[0];
            lensModel_b = markerFrameToLensModelList[1];
        }

        auto success = ::mmsolver::sfm::add_marker_pair_at_frame(
            m_time_a, m_time_b, m_image_width_a, m_image_width_b,
            m_image_height_a, m_image_height_b, lensModel_a, lensModel_b,
            marker_a, marker_b, m_marker_coords_a, m_marker_coords_b);
    }

    MMSOLVER_MAYA_VRB(
        "parse m_marker_coords_a size: " << m_marker_coords_a.size());
    MMSOLVER_MAYA_VRB(
        "parse m_marker_coords_b size: " << m_marker_coords_b.size());
    MMSOLVER_ASSERT(m_marker_coords_a.size() == m_marker_coords_b.size(),
                    "No change in marker count should be possible.");

    return status;
}

MStatus MMMarkerHomographyCmd::doIt(const MArgList &args) {
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

    openMVG::Mat3 homography_matrix;
    auto relative_pose_ok = ::mmsolver::sfm::compute_homography(
        m_image_width_a, m_image_width_b, m_image_height_a, m_image_height_b,
        m_marker_coords_a, m_marker_coords_b, homography_matrix);
    if (!relative_pose_ok) {
        MMSOLVER_MAYA_ERR("Compute Relative pose failed.");
        MMMarkerHomographyCmd::setResult(emptyResult);
        return status;
    }

    // Output 3x3 Matrix to Maya command result.
    for (auto i = 0; i < 3; i++) {
        auto row = homography_matrix.row(i);
        outResult.append(row[0]);
        outResult.append(row[1]);
        outResult.append(row[2]);
    }

    MMMarkerHomographyCmd::setResult(outResult);
    return status;
}

}  // namespace mmsolver
