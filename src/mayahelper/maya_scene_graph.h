/*
 * Copyright (C) 2020, 2021 David Cattermole.
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

#ifndef MAYA_MM_SOLVER_MAYA_SCENE_GRAPH_H
#define MAYA_MM_SOLVER_MAYA_SCENE_GRAPH_H

// Maya
#include <maya/MStreamUtils.h>
#include <maya/MDagPath.h>
#include <maya/MObject.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MComputation.h>
#include <maya/MString.h>

// STL
#include <memory>
#include <vector>
#include <string>

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

// Internal
#include "maya_camera.h"
#include "maya_attr.h"
#include "maya_marker.h"
#include "maya_bundle.h"
#include "maya_utils.h"

MStatus construct_scene_graph(
        CameraPtrList &cameraList,
        MarkerPtrList &markerList,
        BundlePtrList &bundleList,
        AttrPtrList &attrList,
        const MTimeArray &frameList,
        const int timeEvalMode,
        mmscenegraph::SceneGraph &out_sceneGraph,
        mmscenegraph::AttrDataBlock &out_attrDataBlock,
        mmscenegraph::FlatScene &out_flatScene,
        std::vector<mmscenegraph::FrameValue> &out_frameList,
        std::vector<mmscenegraph::CameraNode> &out_cameraNodes,
        std::vector<mmscenegraph::BundleNode> &out_bundleNodes,
        std::vector<mmscenegraph::MarkerNode> &out_markerNodes,
        std::vector<mmscenegraph::AttrId> &out_attrIdList
);

#endif  // MAYA_MM_SOLVER_MAYA_SCENE_GRAPH_H