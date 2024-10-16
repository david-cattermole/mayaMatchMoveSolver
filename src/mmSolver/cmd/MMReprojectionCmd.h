/*
 * Copyright (C) 2019 David Cattermole.
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
 * Header for mmReprojection Maya command.
 */

#ifndef MAYA_MM_REPROJECTION_CMD_H
#define MAYA_MM_REPROJECTION_CMD_H

// STL
#include <cmath>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPoint.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// MM Solver
#include "mmSolver/core/reprojection.h"
#include "mmSolver/mayahelper/maya_camera.h"

// Command arguments and command name:

// World-space Point to reproject, rather than giving a node.
#define WORLD_POINT_FLAG "-wp"
#define WORLD_POINT_FLAG_LONG "-worldPoint"

// Camera to reproject into.
#define CAMERA_FLAG "-c"
#define CAMERA_FLAG_LONG "-camera"

// Image Resolution
#define IMAGE_RES_FLAG "-ir"
#define IMAGE_RES_FLAG_LONG "-imageResolution"

// Time
#define TIME_FLAG "-t"
#define TIME_FLAG_LONG "-time"

// Query as Camera Point?
#define AS_CAM_POINT_FLAG "-cpt"
#define AS_CAM_POINT_FLAG_LONG "-asCameraPoint"

// Query as World Point?
#define AS_WORLD_POINT_FLAG "-wpt"
#define AS_WORLD_POINT_FLAG_LONG "-asWorldPoint"

// Query as Coordinate?
#define AS_COORD_FLAG "-cd"
#define AS_COORD_FLAG_LONG "-asCoordinate"

// Query as Pixel Coordinate?
#define AS_PIXEL_COORD_FLAG "-pcd"
#define AS_PIXEL_COORD_FLAG_LONG "-asPixelCoordinate"

// Query as Normalized Coordinate?
#define AS_NORM_COORD_FLAG "-ncd"
#define AS_NORM_COORD_FLAG_LONG "-asNormalizedCoordinate"

// Query as Normalized Coordinate?
#define AS_MARKER_COORD_FLAG "-mcd"
#define AS_MARKER_COORD_FLAG_LONG "-asMarkerCoordinate"

// Add Camera Direction Ratio to the list of data returned for each
// point.
//
// This is helpful to find out if a transform is behind the camera or
// not.
#define WITH_CAMERA_DIR_RATIO_FLAG "-wcd"
#define WITH_CAMERA_DIR_RATIO_FLAG_LONG "-withCameraDirectionRatio"

// Should the input transform be re-distorted or undistorted?
//
// This will only work if the camera has an 'outLens' attribute, and
// the attribute is connected to a chain of lens nodes (with at least
// one lens node in the chain).
#define DISTORT_MODE_FLAG "-dsm"
#define DISTORT_MODE_FLAG_LONG "-distortMode"

namespace mmsolver {

class MMReprojectionCmd : public MPxCommand {
public:
    MMReprojectionCmd()
        : m_nodeList()
        , m_givenWorldPoint(false)
        , m_worldPoint()
        , m_timeList()
        , m_asCameraPoint(false)
        , m_asWorldPoint(false)
        , m_asCoordinate(false)
        , m_asNormalizedCoordinate(false)
        , m_asMarkerCoordinate(false)
        , m_asPixelCoordinate(false)
        , m_withCameraDirRatio(false)
        , m_distort_mode(ReprojectionDistortMode::kNone)
        , m_cameraPtr(CameraPtr(new Camera())){};

    virtual ~MMReprojectionCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    MSelectionList m_nodeList;
    bool m_givenWorldPoint;
    MPoint m_worldPoint;
    CameraPtr m_cameraPtr;
    MTimeArray m_timeList;
    double m_imageResX;
    double m_imageResY;

    bool m_asCameraPoint;
    bool m_asWorldPoint;
    bool m_asCoordinate;
    bool m_asNormalizedCoordinate;
    bool m_asMarkerCoordinate;
    bool m_asPixelCoordinate;
    bool m_withCameraDirRatio;
    ReprojectionDistortMode m_distort_mode;
};

}  // namespace mmsolver

#endif  // MAYA_MM_REPROJECTION_CMD_H
