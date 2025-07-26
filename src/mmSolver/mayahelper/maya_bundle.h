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
 * Class Bundle, represents a 3D point of a 2D Marker.
 */

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_BUNDLE_H
#define MM_SOLVER_MAYA_HELPER_MAYA_BUNDLE_H

#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPoint.h>
#include <maya/MString.h>

#include <memory>
#include <vector>

#include "maya_attr.h"

class Marker;

class Bundle {
public:
    Bundle();

    MString getNodeName() const;
    MStatus setNodeName(MString value);
    MObject getObject();

    double getWeight() const;
    MStatus setWeight(double value);

    Attr &getMatrixAttr();

    MStatus getMatrix(MMatrix &value, const MTime &time,
                      const int timeEvalMode);
    MStatus getMatrix(MMatrix &value, const int timeEvalMode);

    MStatus getPos(double &x, double &y, double &z, const MTime &time,
                   const int timeEvalMode);
    MStatus getPos(MPoint &point, const MTime &time, const int timeEvalMode);
    MStatus getPos(double &x, double &y, double &z, const int timeEvalMode);
    MStatus getPos(MPoint &point, const int timeEvalMode);

    MString getLongNodeName();

private:
    MString m_nodeName;
    MObject m_object;
    double m_weight;
    Attr m_matrix;
};

typedef std::vector<Bundle> BundleList;
typedef BundleList::iterator BundleListIt;

typedef std::shared_ptr<Bundle> BundlePtr;
typedef std::vector<std::shared_ptr<Bundle> > BundlePtrList;
typedef BundlePtrList::iterator BundlePtrListIt;

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_BUNDLE_H
