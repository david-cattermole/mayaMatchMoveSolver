/*
 * Copyright (C) 2018, 2019, 2023 David Cattermole.
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
 * Class for Marker Group objects, the nodes above Markers, used to
 * scale Markers into Marker space.
 */

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_MARKER_GROUP_H
#define MM_SOLVER_MAYA_HELPER_MAYA_MARKER_GROUP_H

// STL
#include <memory>
#include <vector>

// Maya
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MTime.h>

// MM Solver
#include "maya_attr.h"

class MarkerGroup {
public:
    MarkerGroup();

    MString getNodeName() const;
    MStatus setNodeName(MString value);
    MObject getObject();

    Attr &getDepthAttr();
    Attr &getOverscanXAttr();
    Attr &getOverscanYAttr();

    MStatus getDepth(double &value, const MTime &time,
                     const int32_t timeEvalMode);

    MStatus getOverscanXY(double &x, double &y, const MTime &time,
                          const int32_t timeEvalMode);
    MStatus getOverscanXY(double &x, double &y, const int32_t timeEvalMode);

    MString getLongNodeName();

private:
    MString m_nodeName;
    MObject m_object;

    Attr m_depth;
    Attr m_overscan_x;
    Attr m_overscan_y;
};

typedef std::vector<MarkerGroup> MarkerGroupList;
typedef MarkerGroupList::iterator MarkerGroupListIt;

typedef std::shared_ptr<MarkerGroup> MarkerGroupPtr;
typedef std::vector<std::shared_ptr<MarkerGroup> > MarkerGroupPtrList;
typedef MarkerGroupPtrList::iterator MarkerGroupPtrListIt;
typedef MarkerGroupPtrList::const_iterator MarkerGroupPtrListCIt;

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_MARKER_GROUP_H
