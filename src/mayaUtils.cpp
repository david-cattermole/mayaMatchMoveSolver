/*
 * Copyright (C) 2018, 2019, 2021 David Cattermole.
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
 */

#include <mayaUtils.h>

// Maya
#include <maya/MStatus.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MPxNode.h>
#include <maya/MStreamUtils.h>

MStatus
MMNodeInitUtils::attributeAffectsMulti(
        const MObjectArray &inputAttrs,
        const MObjectArray &outputAttrs)
{
    MStatus status = MS::kSuccess;
    for (unsigned int i = 0; i < inputAttrs.length(); i++) {
        for (unsigned int j = 0; j < outputAttrs.length(); j++) {
            MObject inputAttr = inputAttrs[i];
            MObject outputAttr = outputAttrs[j];
            status = MPxNode::attributeAffects(inputAttr, outputAttr);
            if (status != MS::kSuccess) {
                MStreamUtils::stdErrorStream()
                    << "ERROR: attributeAffects failed at "
                    << "input_index=" << i
                    << " output_index=" << j
                    << '\n';
                CHECK_MSTATUS(status);
            }
        }
    }
    return status;
}
