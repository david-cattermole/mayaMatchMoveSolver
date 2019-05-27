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
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>

#include <maya/MPxCommand.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MSyntax.h>

#include <maya/MSelectionList.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// Internal Objects
#include <Camera.h>

// Command arguments and command name:

// Camera to reproject into.
#define CAMERA_FLAG            "-c"
#define CAMERA_FLAG_LONG       "-camera"

// Image Resolution
#define IMAGE_RES_FLAG       "-ir"
#define IMAGE_RES_FLAG_LONG  "-imageResolution"

// Time
#define TIME_FLAG              "-t"
#define TIME_FLAG_LONG         "-time"

// Query as Camera Point?
#define CAM_POINT_FLAG       "-cpt"
#define CAM_POINT_FLAG_LONG  "-asCameraPoint"

// Query as World Point?
#define WORLD_POINT_FLAG       "-wpt"
#define WORLD_POINT_FLAG_LONG  "-asWorldPoint"

// Query as Coordinate?
#define COORD_FLAG       "-cd"
#define COORD_FLAG_LONG  "-asCoordinate"

// Query as Pixel Coordinate?
#define PIXEL_COORD_FLAG       "-pcd"
#define PIXEL_COORD_FLAG_LONG  "-asPixelCoordinate"

// Query as Normalized Coordinate?
#define NORM_COORD_FLAG       "-ncd"
#define NORM_COORD_FLAG_LONG  "-asNormalizedCoordinate"

// Query as Normalized Coordinate?
#define MARKER_COORD_FLAG       "-mcd"
#define MARKER_COORD_FLAG_LONG  "-asMarkerCoordinate"


class MMReprojectionCmd : public MPxCommand {
public:

    MMReprojectionCmd() : m_nodeList(),
                          m_camera(),
                          m_timeList(),
                          m_asCameraPoint(false),
                          m_asWorldPoint(false),
                          m_asCoordinate(false),
                          m_asNormalizedCoordinate(false),
                          m_asMarkerCoordinate(false),
                          m_asPixelCoordinate(false) {};

    virtual ~MMReprojectionCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs( const MArgList& args );

    MSelectionList m_nodeList;
    Camera m_camera;
    MTimeArray m_timeList;
    double m_imageResX;
    double m_imageResY;

    bool m_asCameraPoint;
    bool m_asWorldPoint;
    bool m_asCoordinate;
    bool m_asNormalizedCoordinate;
    bool m_asMarkerCoordinate;
    bool m_asPixelCoordinate;
};

#endif // MAYA_MM_REPROJECTION_CMD_H
