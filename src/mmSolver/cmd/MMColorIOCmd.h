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
 * Header for mmColorIO Maya command.
 */

#ifndef MAYA_MM_COLOR_IO_CMD_H
#define MAYA_MM_COLOR_IO_CMD_H

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MSyntax.h>

// Command arguments and command name:
#define COLOR_SPACE_EXISTS_FLAG "-ce"
#define COLOR_SPACE_EXISTS_FLAG_LONG "-colorSpaceExists"

#define CONFIG_DESCRIPTION_FLAG "-de"
#define CONFIG_DESCRIPTION_FLAG_LONG "-configDescription"

#define CONFIG_NAME_FLAG "-nm"
#define CONFIG_NAME_FLAG_LONG "-configName"

#define CONFIG_SEARCH_PATH_FLAG "-sp"
#define CONFIG_SEARCH_PATH_FLAG_LONG "-configSearchPath"

#define CONFIG_WORKING_DIRECTORY_FLAG "-wd"
#define CONFIG_WORKING_DIRECTORY_FLAG_LONG "-configWorkingDirectory"

#define GUESS_COLOR_SPACE_FROM_FILE_FLAG "-gc"
#define GUESS_COLOR_SPACE_FROM_FILE_FLAG_LONG "-guessColorSpaceFromFile"

#define LIST_COLOR_SPACES_ACTIVE_FLAG "-la"
#define LIST_COLOR_SPACES_ACTIVE_FLAG_LONG "-listColorSpacesActive"

#define LIST_COLOR_SPACES_ALL_FLAG "-lc"
#define LIST_COLOR_SPACES_ALL_FLAG_LONG "-listColorSpacesAll"

#define LIST_COLOR_SPACES_INACTIVE_FLAG "-li"
#define LIST_COLOR_SPACES_INACTIVE_FLAG_LONG "-listColorSpacesInactive"

// TODO: Add the InterchangeScene and InterchangeDisplay roles?
#define ROLE_COLOR_PICKING_FLAG "-rp"
#define ROLE_COLOR_PICKING_FLAG_LONG "-roleColorPicking"
#define ROLE_COLOR_TIMING_FLAG "-rt"
#define ROLE_COLOR_TIMING_FLAG_LONG "-roleColorTiming"
#define ROLE_COMPOSITING_LOG_FLAG "-rg"
#define ROLE_COMPOSITING_LOG_FLAG_LONG "-roleCompositingLog"
#define ROLE_DATA_FLAG "-ra"
#define ROLE_DATA_FLAG_LONG "-roleData"
#define ROLE_DEFAULT_FLAG "-rd"
#define ROLE_DEFAULT_FLAG_LONG "-roleDefault"
#define ROLE_MATTE_PAINT_FLAG "-ri"
#define ROLE_MATTE_PAINT_FLAG_LONG "-roleMattePaint"
#define ROLE_REFERENCE_FLAG "-rr"
#define ROLE_REFERENCE_FLAG_LONG "-roleReference"
#define ROLE_RENDERING_FLAG "-rn"
#define ROLE_RENDERING_FLAG_LONG "-roleRendering"
#define ROLE_SCENE_LINEAR_FLAG "-rl"
#define ROLE_SCENE_LINEAR_FLAG_LONG "-roleSceneLinear"
#define ROLE_TEXTURE_PAINT_FLAG "-rx"
#define ROLE_TEXTURE_PAINT_FLAG_LONG "-roleTexturePaint"

namespace mmsolver {

class MMColorIOCmd : public MPxCommand {
public:
    MMColorIOCmd()
        : m_color_space_exists(false)
        , m_config_description(false)
        , m_config_name(false)
        , m_config_search_path(false)
        , m_config_working_directory(false)
        , m_guess_color_space_from_file(false)
        , m_list_color_spaces_active(false)
        , m_list_color_spaces_all(false)
        , m_list_color_spaces_inactive(false)
        , m_role_color_picking(false)
        , m_role_color_timing(false)
        , m_role_compositing_log(false)
        , m_role_data(false)
        , m_role_default(false)
        , m_role_matte_paint(false)
        , m_role_reference(false)
        , m_role_rendering(false)
        , m_role_scene_linear(false)
        , m_role_texture_paint(false){};

    virtual ~MMColorIOCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    bool m_color_space_exists;
    bool m_config_description;
    bool m_config_name;
    bool m_config_search_path;
    bool m_config_working_directory;
    bool m_guess_color_space_from_file;
    bool m_list_color_spaces_active;
    bool m_list_color_spaces_all;
    bool m_list_color_spaces_inactive;
    bool m_role_color_picking;
    bool m_role_color_timing;
    bool m_role_compositing_log;
    bool m_role_data;
    bool m_role_default;
    bool m_role_matte_paint;
    bool m_role_reference;
    bool m_role_rendering;
    bool m_role_scene_linear;
    bool m_role_texture_paint;

    MString m_file_path;
    MString m_color_space_name;
};

}  // namespace mmsolver

#endif  // MAYA_MM_COLOR_IO_CMD_H
