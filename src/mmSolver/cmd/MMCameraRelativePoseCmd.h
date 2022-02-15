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
 * Header for mmCameraSolve Maya command.
 */

#ifndef MM_SOLVER_MM_CAMERA_RELATIVE_POSE_CMD_H
#define MM_SOLVER_MM_CAMERA_RELATIVE_POSE_CMD_H

// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxCommand.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MSyntax.h>
#include <maya/MSelectionList.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MDGModifier.h>
#include <maya/MAnimCurveChange.h>

// Maya helpers
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {

class MMCameraRelativePoseCmd : public MPxCommand {
public:

    MMCameraRelativePoseCmd() {};
    virtual ~MMCameraRelativePoseCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);
    virtual bool isUndoable() const;
    virtual MStatus undoIt();
    virtual MStatus redoIt();

    static void *creator();
    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    // OpenMVG
    int32_t m_image_width_a;
    int32_t m_image_height_a;
    int32_t m_image_width_b;
    int32_t m_image_height_b;
    double m_focal_length_mm_a;
    double m_focal_length_mm_b;
    double m_sensor_width_mm_a;
    double m_sensor_height_mm_a;
    double m_sensor_width_mm_b;
    double m_sensor_height_mm_b;
    std::vector<std::pair<double, double>> m_marker_coords_a;
    std::vector<std::pair<double, double>> m_marker_coords_b;

    // Maya Objects
    Camera m_camera_a;
    Attr m_camera_a_tx_attr;
    Attr m_camera_a_ty_attr;
    Attr m_camera_a_tz_attr;
    Attr m_camera_a_rx_attr;
    Attr m_camera_a_ry_attr;
    Attr m_camera_a_rz_attr;

    // Camera m_camera_b;
    // Attr m_camera_b_tx_attr;
    // Attr m_camera_b_ty_attr;
    // Attr m_camera_b_tz_attr;
    // Attr m_camera_b_rx_attr;
    // Attr m_camera_b_ry_attr;
    // Attr m_camera_b_rz_attr;

    // Frame range
    uint32_t m_startFrame;
    uint32_t m_endFrame;
    MTime m_startTime;
    MTime m_endTime;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
};

} // namespace mmsolver

#endif // MM_SOLVER_MM_CAMERA_RELATIVE_POSE_CMD_H
