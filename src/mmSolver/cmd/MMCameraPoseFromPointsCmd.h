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
 * Header for mmCameraPoseFromPoints Maya command.
 */

#ifndef MM_SOLVER_MM_CAMERA_POSE_FROM_POINTS_CMD_H
#define MM_SOLVER_MM_CAMERA_POSE_FROM_POINTS_CMD_H

// STL
#include <cmath>
#include <tuple>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDGModifier.h>
#include <maya/MEulerRotation.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// Maya helpers
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_list.h"
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {

class MMCameraPoseFromPointsCmd : public MPxCommand {
public:
    MMCameraPoseFromPointsCmd() : m_set_values(false){};
    virtual ~MMCameraPoseFromPointsCmd();

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

    bool m_set_values;

    // Maya Objects
    CameraPtr m_camera;
    Attr m_camera_tx_attr;
    Attr m_camera_ty_attr;
    Attr m_camera_tz_attr;
    Attr m_camera_rx_attr;
    Attr m_camera_ry_attr;
    Attr m_camera_rz_attr;
    MEulerRotation::RotationOrder m_camera_rotate_order;

    MarkerList m_marker_list;

    // Frames
    std::vector<uint32_t> m_frames;
    std::vector<MTime> m_times;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_MM_CAMERA_POSE_FROM_POINTS_CMD_H
