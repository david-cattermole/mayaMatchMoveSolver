/*
 * Copyright (C) 2024 David Cattermole.
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
 * Command for running mmColorIO.
 *
 * The mmColorIO command is responsible for querying and setting
 * details about the input/output of colours in mmSolver, for
 * converting colours, images and textures from one colour space to
 * another (using OpenColorIO under the hood).
 *
 * MEL:
 *     // List all known colour spaces.
 *     mmColorIO -listColorSpacesAll
 *
 *     // List all known active colour spaces.
 *     mmColorIO -listColorSpacesActive
 *
 *     // List all known inactive colour spaces.
 *     mmColorIO -listColorSpacesInactive
 *
 *     // Get "scene linear" role colour space.
 *     mmColorIO -roleSceneLinear
 *
 *     // Check if the given colour space exists.
 *     mmColorIO -colorSpaceExists "ACEScg"
 *
 *     // Guess colour space from given file.
 *     mmColorIO -guessColorSpaceFromFile "/path/to/file.jpg"
 *
 *     // Get the current config details.
 *     mmColorIO -configName
 *     mmColorIO -configDescription
 *     mmColorIO -configSearchPath
 *     mmColorIO -configWorkingDirectory
 *
 */

#include "MMColorIOCmd.h"

// STL
#include <cstring>
#include <string>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MFileObject.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MImage.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// MM Solver Libs
#include <mmcolorio/lib.h>

// MM Solver
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/path_utils.h"

namespace mmsolver {

MMColorIOCmd::~MMColorIOCmd() {}

void *MMColorIOCmd::creator() { return new MMColorIOCmd(); }

MString MMColorIOCmd::cmdName() { return MString("mmColorIO"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMColorIOCmd::hasSyntax() const { return true; }

bool MMColorIOCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMColorIOCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(LIST_COLOR_SPACES_ALL_FLAG, LIST_COLOR_SPACES_ALL_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(LIST_COLOR_SPACES_ACTIVE_FLAG,
                   LIST_COLOR_SPACES_ACTIVE_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(LIST_COLOR_SPACES_INACTIVE_FLAG,
                   LIST_COLOR_SPACES_INACTIVE_FLAG_LONG, MSyntax::kBoolean);

    syntax.addFlag(ROLE_DEFAULT_FLAG, ROLE_DEFAULT_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(ROLE_REFERENCE_FLAG, ROLE_REFERENCE_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(ROLE_DATA_FLAG, ROLE_DATA_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(ROLE_COLOR_PICKING_FLAG, ROLE_COLOR_PICKING_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(ROLE_SCENE_LINEAR_FLAG, ROLE_SCENE_LINEAR_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(ROLE_COMPOSITING_LOG_FLAG, ROLE_COMPOSITING_LOG_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(ROLE_COLOR_TIMING_FLAG, ROLE_COLOR_TIMING_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(ROLE_TEXTURE_PAINT_FLAG, ROLE_TEXTURE_PAINT_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(ROLE_MATTE_PAINT_FLAG, ROLE_MATTE_PAINT_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(ROLE_RENDERING_FLAG, ROLE_RENDERING_FLAG_LONG,
                   MSyntax::kBoolean);

    syntax.addFlag(CONFIG_NAME_FLAG, CONFIG_NAME_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(CONFIG_DESCRIPTION_FLAG, CONFIG_DESCRIPTION_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(CONFIG_SEARCH_PATH_FLAG, CONFIG_SEARCH_PATH_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(CONFIG_WORKING_DIRECTORY_FLAG,
                   CONFIG_WORKING_DIRECTORY_FLAG_LONG, MSyntax::kBoolean);

    syntax.addFlag(COLOR_SPACE_EXISTS_FLAG, COLOR_SPACE_EXISTS_FLAG_LONG,
                   MSyntax::kString);

    syntax.addFlag(GUESS_COLOR_SPACE_FROM_FILE_FLAG,
                   GUESS_COLOR_SPACE_FROM_FILE_FLAG_LONG, MSyntax::kString);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMColorIOCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_list_color_spaces_all =
        argData.isFlagSet(LIST_COLOR_SPACES_ALL_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_list_color_spaces_active =
        argData.isFlagSet(LIST_COLOR_SPACES_ACTIVE_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_list_color_spaces_inactive =
        argData.isFlagSet(LIST_COLOR_SPACES_INACTIVE_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_color_picking = argData.isFlagSet(ROLE_COLOR_PICKING_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_color_timing = argData.isFlagSet(ROLE_COLOR_TIMING_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_compositing_log =
        argData.isFlagSet(ROLE_COMPOSITING_LOG_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_data = argData.isFlagSet(ROLE_DATA_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_default = argData.isFlagSet(ROLE_DEFAULT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_matte_paint = argData.isFlagSet(ROLE_MATTE_PAINT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_reference = argData.isFlagSet(ROLE_REFERENCE_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_rendering = argData.isFlagSet(ROLE_RENDERING_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_scene_linear = argData.isFlagSet(ROLE_SCENE_LINEAR_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_role_texture_paint = argData.isFlagSet(ROLE_TEXTURE_PAINT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_config_name = argData.isFlagSet(CONFIG_NAME_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_config_description = argData.isFlagSet(CONFIG_DESCRIPTION_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_config_search_path = argData.isFlagSet(CONFIG_SEARCH_PATH_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_config_working_directory =
        argData.isFlagSet(CONFIG_WORKING_DIRECTORY_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_guess_color_space_from_file =
        argData.isFlagSet(GUESS_COLOR_SPACE_FROM_FILE_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (m_guess_color_space_from_file) {
        status = argData.getFlagArgument(GUESS_COLOR_SPACE_FROM_FILE_FLAG, 0,
                                         m_file_path);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    m_color_space_exists = argData.isFlagSet(COLOR_SPACE_EXISTS_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (m_color_space_exists) {
        status = argData.getFlagArgument(COLOR_SPACE_EXISTS_FLAG, 0,
                                         m_color_space_name);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

MStatus MMColorIOCmd::doIt(const MArgList &args) {
    const bool verbose = false;

    // Read all the flag arguments.
    MStatus status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_list_color_spaces_all || m_list_color_spaces_active ||
        m_list_color_spaces_inactive) {
        auto visibility = mmcolorio::ColorSpaceVisibility::kUnknown;
        if (m_list_color_spaces_all) {
            visibility = mmcolorio::ColorSpaceVisibility::kAll;
        } else if (m_list_color_spaces_active) {
            visibility = mmcolorio::ColorSpaceVisibility::kActive;
        } else if (m_list_color_spaces_inactive) {
            visibility = mmcolorio::ColorSpaceVisibility::kInactive;
        } else {
            MMSOLVER_PANIC("Should not get here.");
        }

        std::vector<std::string> color_space_names =
            mmcolorio::get_color_space_names(visibility);

        MStringArray outResult;
        for (auto i = 0; i < color_space_names.size(); i++) {
            std::string color_space_name = color_space_names[i];
            MMSOLVER_MAYA_VRB("mmColorIO: get color space names: i="
                              << i << "color_space_name=\"" << color_space_name
                              << "\".");

            outResult.append(MString(color_space_name.c_str()));
        }

        // Maya idiosyncrasy: Return None/nothing if a command does
        // not list anything.
        if (outResult.length() > 0) {
            MMColorIOCmd::setResult(outResult);
        }
    } else if (m_role_color_picking || m_role_color_timing ||
               m_role_compositing_log || m_role_data || m_role_default ||
               m_role_matte_paint || m_role_reference || m_role_rendering ||
               m_role_scene_linear || m_role_texture_paint) {
        const char *color_space_name = "";
        if (m_role_color_picking) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kColorPicking);
        } else if (m_role_color_timing) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kColorTiming);
        } else if (m_role_compositing_log) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kCompositingLog);
        } else if (m_role_data) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kData);
        } else if (m_role_default) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kDefault);
        } else if (m_role_matte_paint) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kMattePaint);
        } else if (m_role_reference) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kReference);
        } else if (m_role_rendering) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kRendering);
        } else if (m_role_scene_linear) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kSceneLinear);
        } else if (m_role_texture_paint) {
            color_space_name = mmcolorio::get_role_color_space_name(
                mmcolorio::ColorSpaceRole::kTexturePaint);
        } else {
            MMSOLVER_MAYA_ERR("mmColorIO: The role type to query is invalid!");
            return MStatus::kFailure;
        }

        MMSOLVER_MAYA_VRB("mmColorIO: role name: "
                          << "\"" << color_space_name << "\".");

        MString outResult = MString(color_space_name);

        // Maya idiosyncrasy: Return None/nothing if a command does
        // not list anything.
        if (outResult.length() > 0) {
            MMColorIOCmd::setResult(outResult);
        }
    } else if (m_guess_color_space_from_file) {
        MMSOLVER_MAYA_VRB("mmColorIO: guess color space from file: "
                          << "\"" << m_file_path.asChar() << "\".");

        if (m_file_path.length() > 0) {
            MString resolved_file_path = m_file_path;
            status = mmpath::resolve_input_file_path(resolved_file_path);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            const char *color_space_name =
                mmcolorio::guess_color_space_name_from_file_path(
                    resolved_file_path.asChar());
            MString outResult = MString(color_space_name);

            // Maya idiosyncrasy: Return None/nothing if a command does
            // not list anything.
            if (outResult.length() > 0) {
                MMColorIOCmd::setResult(outResult);
            }
        }
    } else if (m_color_space_exists) {
        MMSOLVER_MAYA_VRB("mmColorIO: color space: "
                          << "\"" << m_color_space_name.asChar() << "\".");

        if (m_color_space_name.length() > 0) {
            const bool exists =
                mmcolorio::color_space_name_exists(m_color_space_name.asChar());
            MMSOLVER_MAYA_VRB("mmColorIO: color space exists: " << exists);

            MMColorIOCmd::setResult(exists);
        }
    } else if (m_config_name) {
        const char *config_name = mmcolorio::get_config_name();
        MMSOLVER_MAYA_VRB("mmColorIO: config name: "
                          << "\"" << config_name << "\".");

        // Maya idiosyncrasy: Return None/nothing if a command does
        // not list anything.
        if (std::strlen(config_name) > 0) {
            MMColorIOCmd::setResult(MString(config_name));
        }
    } else if (m_config_description) {
        const char *config_description = mmcolorio::get_config_description();
        MMSOLVER_MAYA_VRB("mmColorIO: config description: "
                          << "\"" << config_description << "\".");

        // Maya idiosyncrasy: Return None/nothing if a command does
        // not list anything.
        if (std::strlen(config_description) > 0) {
            MMColorIOCmd::setResult(MString(config_description));
        }
    } else if (m_config_search_path) {
        const char *config_search_path = mmcolorio::get_config_search_path();
        MMSOLVER_MAYA_VRB("mmColorIO: config search path: "
                          << "\"" << config_search_path << "\".");

        // Maya idiosyncrasy: Return None/nothing if a command does
        // not list anything.
        if (std::strlen(config_search_path) > 0) {
            MMColorIOCmd::setResult(MString(config_search_path));
        }
    } else if (m_config_working_directory) {
        const char *config_working_directory =
            mmcolorio::get_config_working_directory();
        MMSOLVER_MAYA_VRB("mmColorIO: config working directory: "
                          << "\"" << config_working_directory << "\".");

        // Maya idiosyncrasy: Return None/nothing if a command does
        // not list anything.
        if (std::strlen(config_working_directory) > 0) {
            MMColorIOCmd::setResult(MString(config_working_directory));
        }
    }

    return status;
}

}  // namespace mmsolver
