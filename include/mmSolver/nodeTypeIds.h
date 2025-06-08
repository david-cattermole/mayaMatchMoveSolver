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
 * This file lists the Node Type IDs used in the MM Solver project.
 * All node types must listed here.
 *
 * From the Maya documentation:
 *
 * In Maya, both intrinsic and user-defined Maya Objects are registered and
 * recognized by their type identifier or type id. The basis of the type id
 * system is a tag which is used at run-time to determine how to create and
 * destroy Maya Objects, and how they are to be input/output from/to files.
 * These tag-based identifiers are implemented by the class MTypeId.
 * Use the MTypeId class to create, copy and query Maya Object type identifiers.
 * It is very important to note that these ids are written into the Maya binary
 * file format. So, once an id is assigned to a node or data type it can never
 * be changed while any existing Maya file contains an instance of that node
 * or data type. If a change is made, such files will become unreadable.
 *
 * Thus, even though we provide a range of reserved ids that you can use for
 * internal plug-ins, Autodesk highly recommends that you obtain a globally
 * unique id range (see below) and use ids from this range for all your
 * plug-ins, even internal ones. This can prevent significant headaches later if
 * the plans for your plug-ins change.
 *
 * There are 2 forms of the constructor for this class that can be used
 * depending on whether the plug-in id is internal or globally unique.
 *
 * For plug-ins that will forever be internal to your site use the constructor
 * that takes a single unsigned int parameter. The numeric range 0 - 0x7ffff
 * (524288 ids) has been reserved for such plug-ins.
 *
 * The example plug-ins provided with Maya in the plug-in development kit will
 * use ids in the range 0x80000 - 0xfffff (524288 ids). If you customize one
 * of these example plug-ins, you should change the id to avoid future
 * conflicts.
 *
 * Plug-ins that are intended to be shared between sites will need to have a
 * globally unique id. The Autodesk Developer Network (ADN) will provide such
 * id's in blocks of 256. You will be assigned one or more 24-bit prefixes.
 * Once this has been obtained, used the MTypeId constructor that takes 2
 * unsigned int parameters. The prefix goes in the first parameter, and you
 * are responsible for managing the allocation of the 256 ids that go into
 * the second parameter.
 *
 */

#ifndef MM_SOLVER_NODE_TYPE_IDS_H
#define MM_SOLVER_NODE_TYPE_IDS_H

#define MM_MARKER_SCALE_TYPE_ID 0x0012F180
#define MM_MARKER_SCALE_TYPE_NAME "mmMarkerScale"

#define MM_REPROJECTION_TYPE_ID 0x0012F181
#define MM_REPROJECTION_TYPE_NAME "mmReprojection"

#define MM_CAMERA_CALIBRATE_TYPE_ID 0x0012F198
#define MM_CAMERA_CALIBRATE_TYPE_NAME "mmCameraCalibrate"

#define MM_LINE_INTERSECT_TYPE_ID 0x0012F199
#define MM_LINE_INTERSECT_TYPE_NAME "mmLineIntersect"

#define MM_LINE_BEST_FIT_TYPE_ID 0x0012F19C
#define MM_LINE_BEST_FIT_TYPE_NAME "mmLineBestFit"

#define MM_LINE_POINT_INTERSECT_TYPE_ID 0x0012F19D
#define MM_LINE_POINT_INTERSECT_TYPE_NAME "mmLinePointIntersect"

#define MM_MARKER_GROUP_TRANSFORM_TYPE_ID 0x0012F182
#define MM_MARKER_GROUP_TRANSFORM_TYPE_NAME "mmMarkerGroupTransform"
#define MM_MARKER_GROUP_DRAW_CLASSIFY "drawdb/geometry/transform"

#define MM_RENDERER_STANDARD_NAME "mmRendererStandard"
#define MM_RENDER_GLOBALS_STANDARD_TYPE_ID 0x0012F194
#define MM_RENDER_GLOBALS_STANDARD_TYPE_NAME "mmRenderGlobalsStandard"

#define MM_RENDERER_SILHOUETTE_NAME "mmRendererSilhouette"
#define MM_RENDER_GLOBALS_SILHOUETTE_TYPE_ID 0x0012F18E
#define MM_RENDER_GLOBALS_SILHOUETTE_TYPE_NAME "mmRenderGlobalsSilhouette"

#define MM_SKY_DOME_SHAPE_TYPE_ID 0x0012F195
#define MM_SKY_DOME_SHAPE_TYPE_NAME "mmSkyDomeShape"
#define MM_SKY_DOME_DRAW_CLASSIFY "drawdb/geometry/mmSolver/skyDome"
#define MM_SKY_DOME_DRAW_REGISTRANT_ID "mmSkyDomeNodePlugin"
#define MM_SKY_DOME_SHAPE_SELECTION_TYPE_NAME "mmSkyDomeShapeSelection"
#define MM_SKY_DOME_SHAPE_DISPLAY_FILTER_NAME "mmSkyDomeDisplayFilter"
#define MM_SKY_DOME_SHAPE_DISPLAY_FILTER_LABEL "MM SkyDome"

// Maya Python API "Marker/Bundle" proto-type node.
#define MM_MARKER_BUNDLE_SHAPE_TYPE_ID 0x0012F18C

#define MM_MARKER_SHAPE_TYPE_ID 0x0012F196
#define MM_MARKER_SHAPE_TYPE_NAME "mmMarkerShape"
#define MM_MARKER_DRAW_CLASSIFY "drawdb/geometry/mmSolver/marker"
#define MM_MARKER_DRAW_REGISTRANT_ID "mmMarkerNodePlugin"
#define MM_MARKER_SHAPE_SELECTION_TYPE_NAME "mmMarkerShapeSelection"
#define MM_MARKER_SHAPE_DISPLAY_FILTER_NAME "mmMarkerDisplayFilter"
#define MM_MARKER_SHAPE_DISPLAY_FILTER_LABEL "MM Marker"

#define MM_BUNDLE_SHAPE_TYPE_ID 0x0012F197
#define MM_BUNDLE_SHAPE_TYPE_NAME "mmBundleShape"
#define MM_BUNDLE_DRAW_CLASSIFY "drawdb/geometry/mmSolver/bundle"
#define MM_BUNDLE_DRAW_REGISTRANT_ID "mmBundleNodePlugin"
#define MM_BUNDLE_SHAPE_SELECTION_TYPE_NAME "mmBundleShapeSelection"
#define MM_BUNDLE_SHAPE_DISPLAY_FILTER_NAME "mmBundleDisplayFilter"
#define MM_BUNDLE_SHAPE_DISPLAY_FILTER_LABEL "MM Bundle"

#define MM_LINE_SHAPE_TYPE_ID 0x0012F19A
#define MM_LINE_SHAPE_TYPE_NAME "mmLineShape"
#define MM_LINE_DRAW_CLASSIFY "drawdb/geometry/mmSolver/line"
#define MM_LINE_DRAW_REGISTRANT_ID "mmLineNodePlugin"
#define MM_LINE_SHAPE_SELECTION_TYPE_NAME "mmLineShapeSelection"
#define MM_LINE_SHAPE_DISPLAY_FILTER_NAME "mmLineDisplayFilter"
#define MM_LINE_SHAPE_DISPLAY_FILTER_LABEL "MM Line"

#define MM_IMAGE_PLANE_SHAPE_TYPE_ID 0x0012F187
#define MM_IMAGE_PLANE_SHAPE_TYPE_NAME "mmImagePlaneShape"
#define MM_IMAGE_PLANE_SHAPE_DRAW_CLASSIFY \
    "drawdb/geometry/mmSolver/imagePlane/v1"
#define MM_IMAGE_PLANE_SHAPE_DRAW_REGISTRANT_ID "mmImagePlaneShape"
#define MM_IMAGE_PLANE_SHAPE_SELECTION_TYPE_NAME "mmImagePlaneShapeSelection"
#define MM_IMAGE_PLANE_SHAPE_DISPLAY_FILTER_DRAW_DB_CLASSIFICATION \
    "drawdb/geometry/mmSolver/imagePlane/v1"
#define MM_IMAGE_PLANE_SHAPE_DISPLAY_FILTER_NAME "mmImagePlaneDisplayFilter"
#define MM_IMAGE_PLANE_SHAPE_DISPLAY_FILTER_LABEL "MM ImagePlane (legacy)"

#define MM_IMAGE_PLANE_SHAPE_2_TYPE_ID 0x0012F18F
#define MM_IMAGE_PLANE_SHAPE_2_TYPE_NAME "mmImagePlaneShape2"
#define MM_IMAGE_PLANE_SHAPE_2_DRAW_CLASSIFY \
    "drawdb/geometry/mmSolver/imagePlane/v2"
#define MM_IMAGE_PLANE_SHAPE_2_DRAW_REGISTRANT_ID "mmImagePlaneShape2"
#define MM_IMAGE_PLANE_SHAPE_2_SELECTION_TYPE_NAME "mmImagePlaneShape2Selection"
#define MM_IMAGE_PLANE_SHAPE_2_DISPLAY_FILTER_DRAW_DB_CLASSIFICATION \
    "drawdb/geometry/mmSolver/imagePlane/v2"
#define MM_IMAGE_PLANE_SHAPE_2_DISPLAY_FILTER_NAME "mmImagePlane2DisplayFilter"
#define MM_IMAGE_PLANE_SHAPE_2_DISPLAY_FILTER_LABEL "MM ImagePlane"

#define CAMERA_INFERNO_TYPE_ID 0x0012F183  // Not used in mmSolver.

#define MM_LENS_DATA_TYPE_ID 0x0012F184
#define MM_LENS_DATA_TYPE_NAME "MMLensData"

#define MM_LENS_DEFORMER_TYPE_ID 0x0012F185
#define MM_LENS_EVALUATE_TYPE_ID 0x0012F186
#define MM_LENS_MODEL_TOGGLE_TYPE_ID 0x0012F188
#define MM_LENS_MODEL_3DE_TYPE_ID 0x0012F19B

#define MM_MARKER_TRANSFORM_TYPE_ID 0x0012F189
#define MM_MARKER_TRANSFORM_MATRIX_TYPE_ID 0x0012F18A

#define MM_IMAGE_PLANE_TRANSFORM_TYPE_ID 0x0012F18D
#define MM_IMAGE_PLANE_TRANSFORM_TYPE_NAME "mmImagePlaneTransform"
#define MM_IMAGE_PLANE_TRANSFORM_DRAW_CLASSIFY "drawdb/geometry/transform"

#define MM_IMAGE_SEQUENCE_FRAME_LOGIC_TYPE_ID 0x0012F190
#define MM_IMAGE_SEQUENCE_FRAME_LOGIC_TYPE_NAME "mmImageSequenceFrameLogic"

#define OCGM_IMAGE_PLANE_SHAPE_TYPE_ID 0x0012F18B

#define MM_POINT_FROM_OBJECT_SET_TYPE_ID 0x0012F191
#define MM_POINT_FROM_OBJECT_SET_TYPE_NAME "mmPointFromObjectSet"

#endif  // MM_SOLVER_NODE_TYPE_IDS_H
