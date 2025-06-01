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
#include "mmSolver/core/frame.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_list.h"
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {

class MMCameraRelativePoseCmd : public MPxCommand {
public:
    MMCameraRelativePoseCmd()
        : m_set_values(false)
        , m_image_width_a(1)
        , m_image_height_a(1)
        , m_image_width_b(1)
        , m_image_height_b(1)
        , m_focal_length_mm_a(35.0)
        , m_focal_length_mm_b(35.0)
        , m_sensor_width_mm_a(1.0)
        , m_sensor_height_mm_a(1.0)
        , m_sensor_width_mm_b(1.0)
        , m_sensor_height_mm_b(1.0)
        , m_use_camera_transform(false)
        , m_frame_a(1)
        , m_frame_b(10){};
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

    bool m_set_values;

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
    CameraPtr m_camera_a;
    Attr m_camera_tx_attr_a;
    Attr m_camera_ty_attr_a;
    Attr m_camera_tz_attr_a;
    Attr m_camera_rx_attr_a;
    Attr m_camera_ry_attr_a;
    Attr m_camera_rz_attr_a;

    CameraPtr m_camera_b;
    Attr m_camera_tx_attr_b;
    Attr m_camera_ty_attr_b;
    Attr m_camera_tz_attr_b;
    Attr m_camera_rx_attr_b;
    Attr m_camera_ry_attr_b;
    Attr m_camera_rz_attr_b;

    MEulerRotation::RotationOrder m_camera_rotate_order_a;
    MEulerRotation::RotationOrder m_camera_rotate_order_b;

    bool m_use_camera_transform;
    MMatrix m_camera_transform_matrix;

    MarkerList m_marker_list_a;
    MarkerList m_marker_list_b;
    BundlePtrList m_bundle_list;
    std::vector<double> m_bundle_pos_list;

    // Frames A and B
    FrameNumber m_frame_a;
    FrameNumber m_frame_b;
    MTime m_time_a;
    MTime m_time_b;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_MM_CAMERA_RELATIVE_POSE_CMD_H
