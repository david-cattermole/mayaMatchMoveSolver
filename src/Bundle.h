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

#ifndef MAYA_MM_SOLVER_BUNDLE_H
#define MAYA_MM_SOLVER_BUNDLE_H

#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>
#include <maya/MPlug.h>

#include <vector>
#include <memory>

#include <Attr.h>

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

    MStatus getMatrix(MMatrix &value, const MTime &time);

    MStatus getMatrix(MMatrix &value);

    MStatus getPos(double &x, double &y, double &z, const MTime &time);

    MStatus getPos(MPoint &point, const MTime &time);

    MStatus getPos(double &x, double &y, double &z);

    MStatus getPos(MPoint &point);

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

#endif //MAYA_MM_SOLVER_BUNDLE_H
