/*
 * Copyright (C) 2020 David Cattermole.
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
 * Header for mmSolverAffects Maya command.
 */

#ifndef MM_SOLVER_AFFECTS_CMD_H
#define MM_SOLVER_AFFECTS_CMD_H

// STL
#include <cmath>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPoint.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MSyntax.h>

// MM Solver
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"

// Command arguments:

// The type of mode for the mmSolverAffects command.
#define MODE_FLAG "-md"
#define MODE_FLAG_LONG "-mode"

// Possible values for the 'mode' flag.
#define MODE_VALUE_ADD_ATTRS_TO_MARKERS "addAttrsToMarkers"
#define MODE_VALUE_RETURN_STRING "returnString"

namespace mmsolver {

class MMSolverAffectsCmd : public MPxCommand {
public:
    MMSolverAffectsCmd(){};

    virtual ~MMSolverAffectsCmd();

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

    // The 'mode' of this command.
    MString m_mode;

    // Objects
    CameraPtrList m_cameraList;
    MarkerPtrList m_markerList;
    BundlePtrList m_bundleList;
    AttrPtrList m_attrList;
    StiffAttrsPtrList m_stiffAttrsList;
    SmoothAttrsPtrList m_smoothAttrsList;

    // Undo/Redo
    MDGModifier m_addAttr_dgmod;
    MDGModifier m_setAttr_dgmod;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_AFFECTS_CMD_H
