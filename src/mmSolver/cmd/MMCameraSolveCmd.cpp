/*
 * Copyright (C) 2021 David Cattermole.
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
 * Command for running mmCameraSolve.
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

// Internal
#include "MMCameraSolveCmd.h"

// STL
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <list>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <string>
#include <utility>

// Ceres Solver
#ifdef MMSOLVER_USE_CERES

#pragma warning(push)
// Compiler Warning (level 1) C4251: needs to have dll-interface to be
// used by clients of class.
#pragma warning(disable : 4251)
#include <ceres/ceres.h>
#pragma warning(pop)

#endif  // MMSOLVER_USE_CERES

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <openMVG/numeric/numeric.h>

#include <openMVG/features/feature.hpp>
#include <openMVG/features/feature_container.hpp>
#include <openMVG/matching/indMatch.hpp>
#include <openMVG/matching/regions_matcher.hpp>
#include <openMVG/multiview/conditioning.hpp>
#include <openMVG/multiview/solver_fundamental_kernel.hpp>
#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/types.hpp>

#include "openMVG/cameras/Camera_Common.hpp"
#include "openMVG/cameras/Cameras_Common_command_line_helper.hpp"

#include "openMVG/sfm/pipelines/sfm_features_provider.hpp"
#include "openMVG/sfm/pipelines/sfm_matches_provider.hpp"
#include "openMVG/sfm/sfm_data.hpp"
#include "openMVG/sfm/sfm_data_io.hpp"
#include "openMVG/sfm/sfm_report.hpp"
#include "openMVG/sfm/sfm_view.hpp"
#include "openMVG/system/timer.hpp"
#include "openMVG/types.hpp"

// SfM Engines
#include "openMVG/sfm/pipelines/sequential/sequential_SfM.hpp"
#include "openMVG/sfm/pipelines/sequential/sequential_SfM2.hpp"
#include "openMVG/sfm/pipelines/sequential/SfmSceneInitializerMaxPair.hpp"
#include "openMVG/sfm/pipelines/sequential/SfmSceneInitializerStellar.hpp"
#include "openMVG/sfm/pipelines/global/GlobalSfM_rotation_averaging.hpp"
#include "openMVG/sfm/pipelines/global/GlobalSfM_translation_averaging.hpp"
#include "openMVG/sfm/pipelines/global/sfm_global_engine_relative_motions.hpp"

#endif  // MMSOLVER_USE_OPENMVG

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MItSelectionList.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// MM Solver
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/sfm/camera_relative_pose.h"
#include "mmSolver/sfm/sfm_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {


using MMMarker = Marker;
using MMCamera = Camera;

using KernelType = openMVG::robust::ACKernelAdaptor<
    openMVG::fundamental::kernel::NormalizedEightPointKernel,
    openMVG::fundamental::kernel::SymmetricEpipolarDistanceError,
    openMVG::UnnormalizerT, openMVG::Mat3>;

MMCameraSolveCmd::~MMCameraSolveCmd() {}

void *MMCameraSolveCmd::creator() { return new MMCameraSolveCmd(); }

MString MMCameraSolveCmd::cmdName() { return MString("mmCameraSolve"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMCameraSolveCmd::hasSyntax() const { return true; }

bool MMCameraSolveCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMCameraSolveCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    unsigned int minNumObjects = 0;
    syntax.setObjectType(MSyntax::kSelectionList, minNumObjects);

    syntax.addFlag("-sf", "-startFrame", MSyntax::kUnsigned);
    syntax.addFlag("-ef", "-endFrame", MSyntax::kUnsigned);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMCameraSolveCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_startFrame = 1;
    if (argData.isFlagSet("-sf")) {
        status = argData.getFlagArgument("-sf", 0, m_startFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    m_endFrame = 120;
    if (argData.isFlagSet("-ef")) {
        status = argData.getFlagArgument("-ef", 0, m_endFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto objects = MSelectionList();
    status = argData.getObjects(objects);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    auto uiUnit = MTime::uiUnit();

    // Reset saved data structures.
    m_marker_coords_a.clear();
    m_marker_coords_b.clear();
    m_image_width_a = 1;
    m_image_height_a = 1;
    m_image_width_b = 1;
    m_image_height_b = 1;

    MItSelectionList iter1(objects);
    for (; !iter1.isDone(); iter1.next()) {
        MDagPath nodeDagPath;
        MObject node_obj;

        status = iter1.getDagPath(nodeDagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = iter1.getDependNode(node_obj);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        auto node_name = nodeDagPath.fullPathName();
        // MMSOLVER_INFO("Node name: " << node_name.asChar());

        auto object_type = computeObjectType(node_obj, nodeDagPath);
        if (object_type == ObjectType::kCamera) {
            // Add Cameras
            MMSOLVER_INFO("Camera name: " << node_name.asChar());
            MString transform_node_name = nodeDagPath.fullPathName();

            status = nodeDagPath.extendToShapeDirectlyBelow(0);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MString shape_node_name = nodeDagPath.fullPathName();

            auto cam = MMCamera();
            cam.setTransformNodeName(transform_node_name);
            cam.setShapeNodeName(shape_node_name);

            ::mmsolver::sfm::get_camera_image_res(
                m_startFrame, uiUnit, cam, m_image_width_a,
                m_image_height_a);
            ::mmsolver::sfm::get_camera_image_res(
                m_endFrame, uiUnit, cam, m_image_width_b,
                m_image_height_b);
        }
    }
    MMSOLVER_INFO("image A: " << m_image_width_a << "x" << m_image_height_a);
    MMSOLVER_INFO("image B: " << m_image_width_b << "x" << m_image_height_b);

    // Parse objects into Camera intrinsics and Tracking Markers.
    MItSelectionList iter2(objects);
    for (; !iter2.isDone(); iter2.next()) {
        MDagPath nodeDagPath;
        MObject node_obj;

        status = iter2.getDagPath(nodeDagPath);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        status = iter2.getDependNode(node_obj);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        auto node_name = nodeDagPath.fullPathName();
        // MMSOLVER_INFO("Node name: " << node_name.asChar());

        auto object_type = computeObjectType(node_obj, nodeDagPath);
        if (object_type == ObjectType::kMarker) {
            // Add Markers
            MMSOLVER_INFO("Marker name: " << node_name.asChar());
            auto mkr = MMMarker();
            mkr.setNodeName(node_name);

            double x_a = 0.0;
            double x_b = 0.0;
            double y_a = 0.0;
            double y_b = 0.0;
            bool enable_a = true;
            bool enable_b = true;
            double weight_a = 1.0;
            double weight_b = 1.0;

            MTime startTime = MTime(static_cast<double>(m_startFrame), uiUnit);
            MTime endTime = MTime(static_cast<double>(m_endFrame), uiUnit);

            auto success_a = ::mmsolver::sfm::get_marker_coord(
                startTime, mkr, x_a,
                y_a, weight_a, enable_a);
            auto success_b = ::mmsolver::sfm::get_marker_coord(
                endTime, mkr, x_b, y_b,
                weight_b, enable_b);
            if (success_a && success_b) {
                double xx_a =
                    (x_a + 0.5) * static_cast<double>(m_image_width_a);
                double yy_a =
                    (y_a + 0.5) * static_cast<double>(m_image_height_a);
                double xx_b =
                    (x_b + 0.5) * static_cast<double>(m_image_width_b);
                double yy_b =
                    (y_b + 0.5) * static_cast<double>(m_image_height_b);
                MMSOLVER_INFO("x_a : " << x_a << " y_a : " << y_a);
                MMSOLVER_INFO("xx_a: " << xx_a << " yy_a: " << yy_a);
                MMSOLVER_INFO("x_b : " << x_b << " y_b : " << y_b);
                MMSOLVER_INFO("xx_b: " << xx_b << " yy_b: " << yy_b);
                auto xy_a = std::pair<double, double>{xx_a, yy_a};
                auto xy_b = std::pair<double, double>{xx_b, yy_b};
                m_marker_coords_a.push_back(xy_a);
                m_marker_coords_b.push_back(xy_b);
            }
        }
    }

    return status;
}

MStatus MMCameraSolveCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Read all the flag arguments.
    status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    // Command Outputs
    MDoubleArray outResult;

    MMCameraSolveCmd::setResult(outResult);
    return status;
}

}  // namespace mmsolver
