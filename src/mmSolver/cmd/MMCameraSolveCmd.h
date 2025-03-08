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
 * Header for mmCameraSolve Maya command.
 */

#ifndef MAYA_MM_CAMERA_SOLVE_CMD_H
#define MAYA_MM_CAMERA_SOLVE_CMD_H

// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MStatus.h>
#include <maya/MTime.h>


namespace mmsolver {

class MMCameraSolveCmd : public MPxCommand {
public:
    MMCameraSolveCmd()
        : m_image_width_a(1)
        , m_image_height_a(1)
        , m_image_width_b(1)
        , m_image_height_b(1)
        , m_startFrame(1)
        , m_endFrame(120){};

    virtual ~MMCameraSolveCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    // OpenMVG
    int32_t m_image_width_a;
    int32_t m_image_height_a;
    int32_t m_image_width_b;
    int32_t m_image_height_b;
    std::vector<std::pair<double, double>> m_marker_coords_a;
    std::vector<std::pair<double, double>> m_marker_coords_b;

    // Frame range
    uint32_t m_startFrame;
    uint32_t m_endFrame;
    MTime m_startTime;
    MTime m_endTime;
};

}  // namespace mmsolver

#endif  // MAYA_MM_CAMERA_SOLVE_CMD_H
