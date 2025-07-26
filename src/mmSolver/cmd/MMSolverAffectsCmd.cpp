/*
 * Copyright (C) 2020 David Cattermole.
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
 * Command for running mmSolverAffects.
 *
 * Example usage (MEL):
 *
 *   mmSolverAffects
 *       -camera "camera1" "camera1Shape"
 *       -marker "myMarker" "camera1Shape" "myBundle"
 *       -attr "myBundle.translateX" "None" "None" "None" "None"
 *       -mode "addAttrsToMarkers";
 *
 * Note: The '-frame' argument is not required for this command. This
 * command only works with time-independent data.
 *
 */

#include "MMSolverAffectsCmd.h"

// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MUuid.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/adjust/adjust_consoleLogging.h"
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/adjust/adjust_relationships.h"
#include "mmSolver/adjust/adjust_results.h"
#include "mmSolver/cmd/common_arg_flags.h"
#include "mmSolver/core/matrix_bool_3d.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_list.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

// Command arguments:

// The type of mode for the mmSolverAffects command.
#define MODE_FLAG "-md"
#define MODE_FLAG_LONG "-mode"

// Possible values for the 'mode' flag.
#define MODE_VALUE_ADD_ATTRS_TO_MARKERS "addAttrsToMarkers"
#define MODE_VALUE_RETURN_STRING "returnString"

// The type of mode for the mmSolverAffects command.
#define GRAPH_MODE_FLAG "-gmd"
#define GRAPH_MODE_FLAG_LONG "-graphMode"

// Possible values for the 'graphMode' flag.
#define GRAPH_MODE_VALUE_NORMAL "normal"
#define GRAPH_MODE_VALUE_NODE_NAME "node_name"
#define GRAPH_MODE_VALUE_OBJECT "object"
#define GRAPH_MODE_VALUE_SIMPLE "simple"

namespace mmsolver {

MMSolverAffectsCmd::~MMSolverAffectsCmd() {}

void *MMSolverAffectsCmd::creator() { return new MMSolverAffectsCmd(); }

MString MMSolverAffectsCmd::cmdName() { return MString("mmSolverAffects"); }

bool MMSolverAffectsCmd::hasSyntax() const { return true; }

bool MMSolverAffectsCmd::isUndoable() const { return true; }

MSyntax MMSolverAffectsCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(MODE_FLAG, MODE_FLAG_LONG, MSyntax::kString);
    syntax.addFlag(GRAPH_MODE_FLAG, GRAPH_MODE_FLAG_LONG, MSyntax::kString);

    createSolveFramesSyntax(syntax);
    createSolveObjectSyntax(syntax);
    return syntax;
}

MStatus MMSolverAffectsCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Mode'
    MMSolverAffectsCmd::m_mode = "";
    if (argData.isFlagSet(MODE_FLAG)) {
        status =
            argData.getFlagArgument(MODE_FLAG, 0, MMSolverAffectsCmd::m_mode);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'GraphMode'
    MMSolverAffectsCmd::m_graph_mode = GraphMode::kNodeName;
    if (argData.isFlagSet(GRAPH_MODE_FLAG)) {
        MString value = "";
        status = argData.getFlagArgument(GRAPH_MODE_FLAG, 0, value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        const MString graph_mode_normal = GRAPH_MODE_VALUE_NORMAL;
        const MString graph_mode_name_based = GRAPH_MODE_VALUE_NODE_NAME;
        const MString graph_mode_object = GRAPH_MODE_VALUE_OBJECT;
        const MString graph_mode_simple = GRAPH_MODE_VALUE_SIMPLE;

        if (value == graph_mode_normal) {
            MMSolverAffectsCmd::m_graph_mode = GraphMode::kNormal;
        } else if (value == graph_mode_name_based) {
            MMSolverAffectsCmd::m_graph_mode = GraphMode::kNodeName;
        } else if (value == graph_mode_object) {
            MMSolverAffectsCmd::m_graph_mode = GraphMode::kObject;
        } else if (value == graph_mode_simple) {
            MMSolverAffectsCmd::m_graph_mode = GraphMode::kSimple;
        } else {
            MMSOLVER_MAYA_ERR(
                "mmSolverAffects: Graph mode value given is not supported; '"
                << value.asChar() << "'.");
            return MS::kFailure;
        }

        MMSOLVER_ASSERT(
            MMSolverAffectsCmd::m_graph_mode != GraphMode::kUnspecified,
            "Graph mode must be specified.");
    }

    parseSolveFramesArguments(argData, m_frameList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    parseSolveObjectArguments(argData, m_cameraList, m_markerList, m_bundleList,
                              m_attrList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

/**
 * @brief Create attributes representing the affects relationship,
 * onto the Marker nodes.
 *
 * This is a technique of persistent storage, so that many functions
 * can re-use the (cached) data.
 */
MStatus setAttrsOnMarkers(
    MarkerList &markerList, AttrList &attrList, const FrameList &frameList,
    const mmsolver::MatrixBool3D &markerToAttrToFrameMatrix,
    MDGModifier &addAttr_dgmod, MDGModifier &setAttr_dgmod,
    MAnimCurveChange &curveChange) {
    const bool verbose = false;
    const bool debug = false;
    MMSOLVER_MAYA_VRB("setAttrsOnMarkers");

    MStatus status = MStatus::kSuccess;

    MMSOLVER_MAYA_VRB(
        "mmSolverAffects: setAttrsOnMarkers: "
        "markerList.count_enabled()="
        << markerList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "mmSolverAffects: setAttrsOnMarkers: "
        "markerList.count_disabled()="
        << markerList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "mmSolverAffects: setAttrsOnMarkers: "
        "attrList.count_enabled()="
        << attrList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "mmSolverAffects: setAttrsOnMarkers: "
        "attrList.count_disabled()="
        << attrList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "mmSolverAffects: setAttrsOnMarkers: "
        "frameList.count_enabled()="
        << frameList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "mmSolverAffects: setAttrsOnMarkers: "
        "frameList.count_disabled()="
        << frameList.count_disabled());

    mmsolver::debug::TimestampBenchmark create_attrs_timer =
        mmsolver::debug::TimestampBenchmark();
    mmsolver::debug::TimestampBenchmark create_curve_timer =
        mmsolver::debug::TimestampBenchmark();
    mmsolver::debug::TimestampBenchmark set_keys_timer =
        mmsolver::debug::TimestampBenchmark();

    const double defaultValue = 0;
    const MFnNumericData::Type unitType = MFnNumericData::Type::kByte;

    // Create all attributes.
    if (!debug) {
        MMSOLVER_MAYA_VRB(
            "mmSolverAffects: setAttrsOnMarkers: Create all attributes...");
    } else {
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: setAttrsOnMarkers: Create all attributes...");
        create_attrs_timer.start();
    }

    for (AttrIndex attrIndex = 0; attrIndex < attrList.size(); ++attrIndex) {
        AttrPtr attr = attrList.get_attr(attrIndex);
        MObject attrNodeObject = attr->getObject();
        MFnDependencyNode attrNodeFn(attrNodeObject);
        MObject attrObject = attr->getAttribute();

        MUuid attrUuid = attrNodeFn.uuid(&status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        const MString attrUuidStr = attrUuid.asString();

        MString attrName = "";
        MFnAttribute attrAttrFn(attrObject);
        const MString nodeAttrName = attrAttrFn.name();
        status = constructAttrAffectsName(nodeAttrName, attrUuidStr, attrName);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        for (MarkerIndex markerIndex = 0; markerIndex < markerList.size();
             ++markerIndex) {
            MarkerPtr marker = markerList.get_marker(markerIndex);
            MObject markerObject = marker->getObject();
            MFnDependencyNode markerNodeFn(markerObject);

            MFnNumericAttribute markerAttrFn(markerObject);
            MObject attributeObj = markerAttrFn.create(
                attrName, attrName, unitType, defaultValue, &status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

            const bool hasAttr = markerNodeFn.hasAttribute(attrName, &status);
            if (verbose) {
                const MString markerName = markerNodeFn.name();
                MMSOLVER_MAYA_VRB("mmSolverAffects: setAttrsOnMarkers: hasAttr="
                                  << hasAttr << " markerName=\""
                                  << markerName.asChar() << "\" attrName =\""
                                  << attrName.asChar() << "\".");
            }
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            if (!hasAttr) {
                status = addAttr_dgmod.addAttribute(markerObject, attributeObj);
                MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            }
        }
    }
    addAttr_dgmod.doIt();

    if (debug) {
        create_attrs_timer.stop();
        const double duration_seconds = create_attrs_timer.get_seconds();
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: setAttrsOnMarkers: Create all attributes "
            "completed! "
            << "Time taken " << duration_seconds << " seconds");
    }

    // Set create animation curves for each attribute.
    const Count32 markerCount = markerList.size();
    const Count32 attrCount = attrList.size();
    if (!debug) {
        MMSOLVER_MAYA_VRB(
            "mmSolverAffects: setAttrsOnMarkers: Create animation curves...");
    } else {
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: setAttrsOnMarkers: Create animation curves...");
        create_curve_timer.start();
    }

    for (int32_t markerIndex = 0; markerIndex < markerCount; ++markerIndex) {
        const bool markerEnabled = markerList.get_enabled(markerIndex);
        if (!markerEnabled) {
            continue;
        }
        MarkerPtr marker = markerList.get_marker(markerIndex);

        MObject markerObject = marker->getObject();
        MFnDependencyNode markerNodeFn(markerObject);

        for (int32_t attrIndex = 0; attrIndex < attrCount; ++attrIndex) {
            const bool attrEnabled = attrList.get_enabled(attrIndex);
            if (!attrEnabled) {
                continue;
            }
            AttrPtr attr = attrList.get_attr(attrIndex);

            MObject attrNodeObject = attr->getObject();
            MFnDependencyNode attrNodeFn(attrNodeObject);
            MUuid attrUuid = attrNodeFn.uuid(&status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            MString attrUuidStr = attrUuid.asString();
            MObject attrObject = attr->getAttribute();

            MString attrName = "";
            MFnAttribute attrFn(attrObject);
            MString nodeAttrName = attrFn.name();
            status =
                constructAttrAffectsName(nodeAttrName, attrUuidStr, attrName);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

            bool wantNetworkedPlug = true;
            MPlug attrPlug =
                markerNodeFn.findPlug(attrName, wantNetworkedPlug, &status);

            const int plugValue = 1;
            status = setAttr_dgmod.newPlugValueInt(attrPlug, plugValue);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

            MFnAnimCurve fnAnimCurve(attrPlug, &status);
            if (status == MS::kNotFound) {
                // Because we must ensure that an animation curve
                // object is connected to the plug, so we can set
                // keyframes on it.
                fnAnimCurve.create(attrPlug, MFnAnimCurve::kAnimCurveTU,
                                   /*modifier=*/&setAttr_dgmod, &status);
                MMSOLVER_MAYA_VRB("mmSolverAffects: setAttrsOnMarkers:"
                                  << " markerIndex: " << markerIndex
                                  << " markerEnabled: " << markerEnabled
                                  << " attrIndex: " << attrIndex
                                  << " attrEnabled: " << attrEnabled
                                  << " ANIM CURVE CREATED.");
            } else {
                MMSOLVER_MAYA_VRB("mmSolverAffects: setAttrsOnMarkers:"
                                  << " markerIndex: " << markerIndex
                                  << " markerEnabled: " << markerEnabled
                                  << " attrIndex: " << attrIndex
                                  << " attrEnabled: " << attrEnabled
                                  << " ANIM CURVE FOUND.");
            }
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }
    setAttr_dgmod.doIt();

    if (debug) {
        create_curve_timer.stop();
        const double duration_seconds = create_curve_timer.get_seconds();
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: setAttrsOnMarkers: Create animation curves "
            "completed! "
            << "Time taken " << duration_seconds << " seconds");
    }

    // Set keyframes on each animation curve based on the valid frame
    // numbers.
    if (!debug) {
        MMSOLVER_MAYA_VRB(
            "mmSolverAffects: setAttrsOnMarkers: Set Keyframes...");
    } else {
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: setAttrsOnMarkers: Set Keyframes...");
        set_keys_timer.start();
    }

    const MTime::Unit uiunit = MTime::uiUnit();
    const Count32 frameCount = frameList.size();
    const Count32 frameEnabledCount = frameList.count_enabled();

    // Reusable array.
    MTimeArray timeArray;
    MDoubleArray valueArray;
    timeArray.setLength(frameEnabledCount);
    valueArray.setLength(frameEnabledCount);

    for (MarkerIndex markerIndex = 0; markerIndex < markerCount;
         ++markerIndex) {
        const bool markerEnabled = markerList.get_enabled(markerIndex);
        if (!markerEnabled) {
            const FrameIndex frameIndex = -1;
            const bool frameEnabled = false;
            const AttrIndex attrIndex = -1;
            const bool attrEnabled = false;
            MMSOLVER_MAYA_VRB("mmSolverAffects: setAttrsOnMarkers:"
                              << " markerIndex: " << markerIndex
                              << " markerEnabled: " << markerEnabled
                              << " attrIndex: " << attrIndex << " attrEnabled: "
                              << attrEnabled << " frameIndex: " << frameIndex
                              << " frameEnabled: " << frameEnabled
                              << " NO KEYFRAME.");
            continue;
        }

        MarkerPtr marker = markerList.get_marker(markerIndex);
        MObject markerObject = marker->getObject();
        MFnDependencyNode markerNodeFn(markerObject);
        // MString markerName = markerNodeFn.name();

        for (AttrIndex attrIndex = 0; attrIndex < attrCount; ++attrIndex) {
            const bool attrEnabled = attrList.get_enabled(attrIndex);
            if (!attrEnabled) {
                const FrameIndex frameIndex = -1;
                const bool frameEnabled = false;
                MMSOLVER_MAYA_VRB("mmSolverAffects: setAttrsOnMarkers:"
                                  << " markerIndex: " << markerIndex
                                  << " markerEnabled: " << markerEnabled
                                  << " attrIndex: " << attrIndex
                                  << " attrEnabled: " << attrEnabled
                                  << " frameIndex: " << frameIndex
                                  << " frameEnabled: " << frameEnabled
                                  << " NO KEYFRAME.");
                continue;
            }

            AttrPtr attr = attrList.get_attr(attrIndex);

            MObject attrNodeObject = attr->getObject();
            MFnDependencyNode attrNodeFn(attrNodeObject);
            MUuid attrUuid = attrNodeFn.uuid(&status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            MString attrUuidStr = attrUuid.asString();
            MObject attrObject = attr->getAttribute();

            MString attrName = "";
            MFnAttribute attrFn(attrObject);
            MString nodeAttrName = attrFn.name();
            status =
                constructAttrAffectsName(nodeAttrName, attrUuidStr, attrName);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

            bool wantNetworkedPlug = true;
            MPlug attrPlug =
                markerNodeFn.findPlug(attrName, wantNetworkedPlug, &status);

            MFnAnimCurve fnAnimCurve(attrPlug, &status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

            Count32 counter = 0;
            for (FrameIndex frameIndex = 0; frameIndex < frameCount;
                 ++frameIndex) {
                const bool frameEnabled = frameList.get_enabled(frameIndex);
                if (!frameEnabled) {
                    MMSOLVER_MAYA_VRB("mmSolverAffects: setAttrsOnMarkers:"
                                      << " markerIndex: " << markerIndex
                                      << " markerEnabled: " << markerEnabled
                                      << " attrIndex: " << attrIndex
                                      << " attrEnabled: " << attrEnabled
                                      << " frameIndex: " << frameIndex
                                      << " frameEnabled: " << frameEnabled
                                      << " NO KEYFRAME.");
                    continue;
                }

                const FrameNumber frameNumber = frameList.get_frame(frameIndex);

                const bool value = markerToAttrToFrameMatrix.at(
                    markerIndex, attrIndex, frameIndex);
                valueArray.set(static_cast<double>(value), counter);

                const MTime frame =
                    MTime(static_cast<double>(frameNumber), uiunit);
                timeArray.set(frame, counter);

                MMSOLVER_MAYA_VRB("mmSolverAffects: setAttrsOnMarkers:"
                                  << " markerIndex: " << markerIndex
                                  << " markerEnabled: " << markerEnabled
                                  << " attrIndex: " << attrIndex
                                  << " attrEnabled: " << attrEnabled
                                  << " frameIndex: " << frameIndex
                                  << " frameEnabled: " << frameEnabled
                                  << " value: " << value << " SET KEYFRAME.");

                counter++;
            }

            // Frames must be cleared so we can add new keyframes.
            for (uint32_t i = 0; i < fnAnimCurve.numKeys(); ++i) {
                fnAnimCurve.remove(0  // , &curveChange
                );
            }

            // Maya API docs say this is better for performance.
            const bool keepExistingKeys = false;

            const auto tangentInType = MFnAnimCurve::kTangentGlobal;
            const auto tangentOutType = MFnAnimCurve::kTangentGlobal;

            // NOTE: Although this is (currently) the fastest known
            // API method for creating batches of keyframes there are
            // still problems with performance. We could remove the curveChange
            status = fnAnimCurve.addKeys(&timeArray, &valueArray, tangentInType,
                                         tangentOutType, keepExistingKeys  // ,
                                         // &curveChange
            );
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }

    if (debug) {
        set_keys_timer.stop();
        const double duration_seconds = set_keys_timer.get_seconds();
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: setAttrsOnMarkers: Set Keyframes completed! "
            << "Time taken " << duration_seconds << " seconds");
    }

    return status;
}

MStatus MMSolverAffectsCmd::doIt(const MArgList &args) {
    const bool verbose = false;
    const bool debug = false;

    // Read all the flag arguments.
    MStatus status = MMSolverAffectsCmd::parseArgs(args);
    if (status != MStatus::kSuccess) {
        MMSOLVER_MAYA_ERR("Error parsing mmSolverAffects command arguments.");
        return status;
    }

    mmsolver::debug::TimestampBenchmark timer =
        mmsolver::debug::TimestampBenchmark();
    timer.start();

    console_log_separator_line();
    MMSOLVER_MAYA_INFO("Analysing Scene... ");
    MMSOLVER_MAYA_INFO("- Marker count: " << m_markerList.size());
    MMSOLVER_MAYA_INFO("- Attribute Count: " << m_attrList.size());
    MMSOLVER_MAYA_INFO("- Frame Count: " << m_frameList.size());

    mmsolver::MatrixBool3D markerToAttrToFrameMatrix;
    if (MMSolverAffectsCmd::m_graph_mode == GraphMode::kNormal) {
        MMSOLVER_MAYA_VRB("mmSolverAffects: Graph Analysis (normal mode)...");

        mmsolver::debug::TimestampBenchmark graph_timer =
            mmsolver::debug::TimestampBenchmark();
        graph_timer.start();

        analyseDependencyGraphRelationships(m_markerList, m_attrList,
                                            m_frameList,

                                            // Outputs
                                            markerToAttrToFrameMatrix, status);

        if (debug) {
            graph_timer.stop();
            const double duration_seconds = graph_timer.get_seconds();
            MMSOLVER_MAYA_INFO(
                "mmSolverAffects: Graph Analysis (normal mode) completed! "
                << "Time taken " << duration_seconds << " seconds");
        }

        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    } else if (MMSolverAffectsCmd::m_graph_mode == GraphMode::kNodeName) {
        MMSOLVER_MAYA_VRB(
            "mmSolverAffects: Graph Analysis (node name mode)...");

        mmsolver::debug::TimestampBenchmark graph_timer =
            mmsolver::debug::TimestampBenchmark();
        graph_timer.start();

        analyseNodeNameRelationships(m_markerList, m_attrList, m_frameList,

                                     // Outputs
                                     markerToAttrToFrameMatrix, status);

        if (debug) {
            graph_timer.stop();
            const double duration_seconds = graph_timer.get_seconds();
            MMSOLVER_MAYA_INFO(
                "mmSolverAffects: Graph Analysis (node name mode) completed! "
                << "Time taken " << duration_seconds << " seconds");
        }

        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    } else if (MMSolverAffectsCmd::m_graph_mode == GraphMode::kObject) {
        MMSOLVER_MAYA_VRB("mmSolverAffects: Graph Analysis (object mode)...");

        mmsolver::debug::TimestampBenchmark graph_timer =
            mmsolver::debug::TimestampBenchmark();
        graph_timer.start();

        analyseObjectRelationships(m_markerList, m_attrList, m_frameList,

                                   // Outputs
                                   markerToAttrToFrameMatrix, status);

        if (debug) {
            graph_timer.stop();
            const double duration_seconds = graph_timer.get_seconds();
            MMSOLVER_MAYA_INFO(
                "mmSolverAffects: Graph Analysis (object mode) completed! "
                << "Time taken " << duration_seconds << " seconds");
        }

        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    } else if (MMSolverAffectsCmd::m_graph_mode == GraphMode::kSimple) {
        MMSOLVER_MAYA_VRB("mmSolverAffects: Graph Analysis (simple mode)...");

        mmsolver::debug::TimestampBenchmark graph_timer =
            mmsolver::debug::TimestampBenchmark();
        graph_timer.start();

        analyseSimpleRelationships(m_markerList, m_attrList, m_frameList,

                                   // Outputs
                                   markerToAttrToFrameMatrix, status);

        if (debug) {
            graph_timer.stop();
            const double duration_seconds = graph_timer.get_seconds();
            MMSOLVER_MAYA_INFO(
                "mmSolverAffects: Graph Analysis (simple mode) completed! "
                << "Time taken " << duration_seconds << " seconds");
        }

        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        MMSOLVER_MAYA_ERR(
            "mmSolverAffects: Graph mode is invalid;"
            << static_cast<uint8_t>(MMSolverAffectsCmd::m_graph_mode));
        return status;
    }

    // To help the developer analyse the quality of the relationships
    // matrix that was generated.
    if (debug) {
        const Count32 markerCount = markerToAttrToFrameMatrix.width();
        const Count32 attrCount = markerToAttrToFrameMatrix.height();
        const Count32 frameCount = markerToAttrToFrameMatrix.depth();

        Count32 enabled = 0;
        for (MarkerIndex markerIndex = 0; markerIndex < markerCount;
             ++markerIndex) {
            for (AttrIndex attrIndex = 0; attrIndex < attrCount; ++attrIndex) {
                for (FrameIndex frameIndex = 0; frameIndex < frameCount;
                     ++frameIndex) {
                    enabled +=
                        static_cast<Count32>(markerToAttrToFrameMatrix.at(
                            markerIndex, attrIndex, frameIndex));
                }
            }
        }
        const Count32 disabled = markerToAttrToFrameMatrix.size() - enabled;

        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: "
            "markerToAttrToFrameMatrix.width="
            << markerCount);
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: "
            "markerToAttrToFrameMatrix.height="
            << attrCount);
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: "
            "markerToAttrToFrameMatrix.depth="
            << frameCount);
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: "
            "markerToAttrToFrameMatrix.size="
            << markerToAttrToFrameMatrix.size());
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: "
            "markerToAttrToFrameMatrix enabled="
            << enabled);
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: "
            "markerToAttrToFrameMatrix disabled="
            << disabled);

        const float ratio =
            static_cast<float>(enabled) /
            static_cast<float>(markerToAttrToFrameMatrix.size());
        MMSOLVER_MAYA_INFO(
            "mmSolverAffects: "
            "markerToAttrToFrameMatrix enabled ratio="
            << ratio);
    }

    // Create 'valid' lists.
    {
        MMSOLVER_MAYA_VRB("mmSolverAffects: Running Solver Object Validity...");

        mmsolver::debug::TimestampBenchmark validity_timer =
            mmsolver::debug::TimestampBenchmark();
        validity_timer.start();

        generateValidMarkerAttrFrameLists(
            m_markerList, m_attrList, m_frameList, markerToAttrToFrameMatrix,

            // Outputs
            m_validMarkerList, m_validAttrList, m_validFrameList, status);

        if (debug) {
            validity_timer.stop();
            const double duration_seconds = validity_timer.get_seconds();
            MMSOLVER_MAYA_INFO(
                "mmSolverAffects: Running Solver Object Validity completed! "
                << "Time taken " << duration_seconds << " seconds");
        }

        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (m_mode == MODE_VALUE_ADD_ATTRS_TO_MARKERS) {
        // TODO: The majority of time spent in this command is spent
        // setting marker attributes, especially for large solves.
        // Therefore this area is the next part to optimize.
        MMSOLVER_MAYA_VRB(
            "mmSolverAffects: Setting Marker Validity Attributes...");

        mmsolver::debug::TimestampBenchmark set_attrs_timer =
            mmsolver::debug::TimestampBenchmark();
        set_attrs_timer.start();

        status =
            setAttrsOnMarkers(m_validMarkerList, m_validAttrList,
                              m_validFrameList, markerToAttrToFrameMatrix,
                              m_addAttr_dgmod, m_setAttr_dgmod, m_curveChange);

        if (debug) {
            set_attrs_timer.stop();
            const double duration_seconds = set_attrs_timer.get_seconds();
            MMSOLVER_MAYA_INFO(
                "mmSolverAffects: Setting Marker Validity Attributes "
                "completed! "
                << "Time taken " << duration_seconds << " seconds");
        }

        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    } else if (m_mode == MODE_VALUE_RETURN_STRING) {
        MMSOLVER_MAYA_VRB("mmSolverAffects: Log Affects Results...");

        mmsolver::debug::TimestampBenchmark log_timer =
            mmsolver::debug::TimestampBenchmark();
        log_timer.start();

        AffectsResult affectsResult;
        status = logResultsMarkerAffectsAttribute(
            m_validMarkerList, m_validAttrList, affectsResult);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        if (debug) {
            log_timer.stop();
            const double duration_seconds = log_timer.get_seconds();
            MMSOLVER_MAYA_INFO(
                "mmSolverAffects: Log Affects Results completed! "
                << "Time taken " << duration_seconds << " seconds");
        }

        MStringArray outResult;
        affectsResult.appendToMStringArray(outResult);
        MMSolverAffectsCmd::setResult(outResult);
    } else {
        MMSOLVER_MAYA_ERR(
            "mmSolverAffects: Mode value is invalid: mode=" << m_mode << "\n");
        status = MS::kFailure;
    }

    timer.stop();
    const double duration_seconds = timer.get_seconds();
    MMSOLVER_MAYA_INFO("Analysing Scene completed! " << "Total time taken "
                                                     << duration_seconds
                                                     << " seconds");
    return status;
}

MStatus MMSolverAffectsCmd::redoIt() {
    MStatus status;
    m_addAttr_dgmod.doIt();
    m_setAttr_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMSolverAffectsCmd::undoIt() {
    MStatus status;
    m_setAttr_dgmod.undoIt();
    m_addAttr_dgmod.undoIt();
    m_curveChange.undoIt();
    return status;
}

}  // namespace mmsolver
