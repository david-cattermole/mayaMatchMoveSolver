/*
 * Copyright (C) 2018, 2019 David Cattermole.
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
 * Class for 2D Marker objects, aka 'track points' or '2d points'.
 */

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_MARKER_H
#define MM_SOLVER_MAYA_HELPER_MAYA_MARKER_H

#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>

#include <memory>
#include <vector>

#include "maya_attr.h"

class Camera;

class Bundle;

class MarkerGroup;

class Marker {
public:
    Marker();

    MString getNodeName() const;
    MStatus setNodeName(MString value);
    MObject getObject();

    std::shared_ptr<Camera> getCamera();
    std::shared_ptr<Bundle> getBundle();
    std::shared_ptr<MarkerGroup> getMarkerGroup();

    MStatus setCamera(std::shared_ptr<Camera> &value);
    MStatus setBundle(std::shared_ptr<Bundle> &value);
    MStatus setMarkerGroup(std::shared_ptr<MarkerGroup> &value);

    Attr &getMatrixAttr();
    Attr &getPosXAttr();
    Attr &getPosYAttr();
    Attr &getEnableAttr();
    Attr &getWeightAttr();

    MStatus getMatrix(MMatrix &value, const MTime &time,
                      const int timeEvalMode);
    MStatus getMatrix(MMatrix &value, const int timeEvalMode);

    MStatus getPos(double &x, double &y, double &z, const MTime &time,
                   const int timeEvalMode);
    MStatus getPos(MPoint &point, const MTime &time, const int timeEvalMode);
    MStatus getPos(double &x, double &y, double &z, const int timeEvalMode);
    MStatus getPos(MPoint &point, const int timeEvalMode);

    MStatus getPosXY(double &out_x, double &out_y, const MTime &time,
                     const int timeEvalMode, const bool applyOverscan = true);
    MStatus getPosXY(double &out_x, double &out_y, const int timeEvalMode,
                     const bool applyOverscan = true);

    MStatus getEnable(bool &value, const MTime &time, const int timeEvalMode);
    MStatus getWeight(double &value, const MTime &time, const int timeEvalMode);

    MString getLongNodeName();

private:
    MString m_nodeName;
    MObject m_object;

    std::shared_ptr<Camera> m_camera;
    std::shared_ptr<Bundle> m_bundle;
    std::shared_ptr<MarkerGroup> m_markerGroup;

    Attr m_matrix;
    Attr m_px;
    Attr m_py;
    Attr m_enable;
    Attr m_weight;
};

typedef std::shared_ptr<Marker> MarkerPtr;
typedef std::vector<std::shared_ptr<Marker> > MarkerPtrList;
typedef MarkerPtrList::iterator MarkerPtrListIt;
typedef MarkerPtrList::const_iterator MarkerPtrListCIt;

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_MARKER_H
