/*
 * Copyright (C) 2023 Patcha Saheb Binginapalli.
 * Copyright (C) 2023, 2024 David Cattermole.
 *
 * Patcha Saheb Binginapalli Python code was ported to C++ by David
 * Cattermole (2023-09-13 YYYY-MM-DD).
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

#include "SilhouetteRender.h"

// Maya
#include <maya/M3dView.h>
#include <maya/MDagPath.h>
#include <maya/MDrawContext.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MGL.h>
#include <maya/MGLFunctionTable.h>
#include <maya/MGeometryExtractor.h>
#include <maya/MGlobal.h>
#include <maya/MHWGeometry.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MHardwareRenderer.h>
#include <maya/MItDag.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MSelectionList.h>
#include <maya/MShaderManager.h>
#include <maya/MStateManager.h>
#include <maya/MString.h>
#include <maya/MTextureManager.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/ops/scene_utils.h"

namespace mmsolver {
namespace render {

SilhouetteRender::SilhouetteRender(const MString& name)
    : MUserRenderOperation(name)
    , m_shader_program(0)
    , m_output_targets(nullptr)
    , m_silhouette_cull_face(GL_BACK)
    , m_silhouette_override_color(false)
    , gGLFT(nullptr) {}

SilhouetteRender::~SilhouetteRender() {
    if (gGLFT && m_shader_program) {
        gGLFT->glDeletePrograms(1, &m_shader_program);
    }
    m_output_targets = nullptr;
}

const char* VERTEX_SHADER_SOURCE =
    "#version 330 core\n"
    "uniform mat4 model_view_projection;\n"
    "layout (location = 0) in vec3 a_position;\n"
    "void main()\n"
    "{\n"
    "    gl_Position = model_view_projection * vec4(a_position, 1.0);\n"
    "}\n";

const char* FRAGMENT_SHADER_SOURCE =
    "#version 330 core\n"
    "uniform vec4 color_alpha;\n"
    "out vec4 out_color;\n"
    "void main()\n"
    "{\n"
    "    out_color = color_alpha;\n"
    "}\n";

GLuint build_shader_program(MGLFunctionTable* gGLFT) {
    MGLint success = 0;

    // Log data.
    const MGLsizei logLengthMax = 512;
    MGLcharARB logTextBlock[logLengthMax];
    MGLsizei* logLengthPtr = nullptr;

    // Vertex shader.
    MGLhandleARB vertexShader =
        gGLFT->glCreateShaderObjectARB(MGL_VERTEX_SHADER_ARB);
    gGLFT->glShaderSourceARB(vertexShader, 1, &VERTEX_SHADER_SOURCE, nullptr);
    gGLFT->glCompileShaderARB(vertexShader);

    // Check for shader compile errors
    gGLFT->glGetObjectParameterivARB(vertexShader,
                                     MGL_OBJECT_COMPILE_STATUS_ARB, &success);
    if (!success) {
        gGLFT->glGetInfoLogARB(vertexShader, logLengthMax, logLengthPtr,
                               logTextBlock);
        MMSOLVER_MAYA_ERR("OpenGL GLSL vertex shader compilation failed:\n"
                          << logTextBlock);
    }

    // Fragment (pixel) shader.
    MGLhandleARB fragmentShader =
        gGLFT->glCreateShaderObjectARB(MGL_FRAGMENT_SHADER_ARB);
    gGLFT->glShaderSourceARB(fragmentShader, 1, &FRAGMENT_SHADER_SOURCE,
                             logLengthPtr);
    gGLFT->glCompileShaderARB(fragmentShader);

    // Check for shader compile errors
    gGLFT->glGetObjectParameterivARB(fragmentShader,
                                     MGL_OBJECT_COMPILE_STATUS_ARB, &success);
    if (!success) {
        gGLFT->glGetInfoLogARB(fragmentShader, logLengthMax, logLengthPtr,
                               logTextBlock);
        MMSOLVER_MAYA_ERR("OpenGL GLSL Fragment shader compilation failed:\n"
                          << logTextBlock);
    }

    // Link shaders.
    MGLhandleARB shader_program = gGLFT->glCreateProgramObjectARB();
    gGLFT->glAttachObjectARB(shader_program, vertexShader);
    gGLFT->glAttachObjectARB(shader_program, fragmentShader);
    gGLFT->glLinkProgramARB(shader_program);

    // Check for linking errors.
    gGLFT->glGetObjectParameterivARB(shader_program, MGL_OBJECT_LINK_STATUS_ARB,
                                     &success);
    if (!success) {
        gGLFT->glGetInfoLogARB(shader_program, logLengthMax, logLengthPtr,
                               logTextBlock);
        MMSOLVER_MAYA_ERR("OpenGL GLSL shader program linking failed:\n"
                          << logTextBlock);
    }
    // After the shader program is linked, we don't need the vertex or
    // fragment shaders.
    gGLFT->glDeleteObjectARB(vertexShader);
    gGLFT->glDeleteObjectARB(fragmentShader);

    return shader_program;
}

MStatus calculate_model_view_projection_matrix(
    M3dView view, MDagPath dag_path, MMatrix& projection_matrix,
    MMatrix& out_model_view_projection) {
    const MMatrix inclusive_matrix = dag_path.inclusiveMatrix();

    // The camera and geometry matrices must be updated each frame,
    // when playblasting. This is not obvious when viewing in the
    MStatus status = MStatus::kSuccess;
    status = view.updateViewingParameters();
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MMatrix model_view_matrix;
    status = view.modelViewMatrix(model_view_matrix);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    out_model_view_projection =
        inclusive_matrix * model_view_matrix * projection_matrix;
    return status;
}

MStatus draw_buffers(
    MGLFunctionTable* gGLFT, const MGLfloat silhouette_color[3],
    const MGLfloat silhouette_alpha, const MGLfloat silhouette_width,
    const MGLfloat silhouette_depth_offset, const MGLenum silhouette_cull_face,
    const MGLfloat default_line_width, const MMatrix& mvp_matrix,
    const MGLuint* vertex_buffer_handle,
    const MGLuint* edge_index_buffer_handle,
    const MGLuint* triangles_index_buffer_handle,
    const MIndexBuffer& edge_index_buffer,
    const MIndexBuffer& triangles_index_buffer, const GLuint shader_program) {
    // Bind buffers
    gGLFT->glBindBufferARB(MGL_ARRAY_BUFFER_ARB, *vertex_buffer_handle);
    // Tell OpenGL how to index into the bound vertex_buffer_handle
    // data.
    gGLFT->glVertexAttribPointer(0, 3, MGL_FLOAT, MGL_FALSE, 0, (void*)0);
    gGLFT->glEnableVertexAttribArray(0);

    // Get uniform locations
    const GLint mvp_location =
        gGLFT->glGetUniformLocationARB(shader_program, "model_view_projection");
    const GLint color_location =
        gGLFT->glGetUniformLocationARB(shader_program, "color_alpha");

    // Use the shader program
    gGLFT->glUseProgramObjectARB(shader_program);

    // Pass the model_view_projection matrix to the shader
    MGLfloat mvp_values[4][4] = {
        {1.0f, 0.0f, 0.0f, 0.0f},
        {0.0f, 1.0f, 0.0f, 0.0f},
        {0.0f, 0.0f, 1.0f, 0.0f},
        {0.0f, 0.0f, 0.0f, 1.0f},
    };
    MStatus status = mvp_matrix.get(mvp_values);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    gGLFT->glUniformMatrix4fvARB(mvp_location, 1, MGL_FALSE, &mvp_values[0][0]);

    // Pass color and alpha as uniforms to the shader
    gGLFT->glUniform4fARB(color_location, silhouette_color[0],
                          silhouette_color[1], silhouette_color[2],
                          silhouette_alpha);

    // Pre draw
    {
        // Enable blending
        gGLFT->glEnable(MGL_BLEND);
        gGLFT->glBlendFunc(MGL_SRC_ALPHA, MGL_ONE_MINUS_SRC_ALPHA);

        // Anti-Aliasing needed for smooth silhouettes to be drawn.
        gGLFT->glEnable(MGL_LINE_SMOOTH);
        gGLFT->glEnable(MGL_MULTISAMPLE);
        gGLFT->glHint(MGL_LINE_SMOOTH_HINT, GL_NICEST);

        gGLFT->glEnable(MGL_CULL_FACE);
        gGLFT->glEnable(MGL_DEPTH_TEST);
        gGLFT->glEnable(MGL_POLYGON_OFFSET_FILL);

        gGLFT->glLineWidth(silhouette_width);
    }

    // Draw Triangles into the depth buffer, with a depth
    // "polygon" offset.
    gGLFT->glColorMask(MGL_FALSE, MGL_FALSE, MGL_FALSE, MGL_FALSE);
    gGLFT->glPolygonOffset(silhouette_width * silhouette_depth_offset, -1.0);
    gGLFT->glPolygonMode(MGL_FRONT_AND_BACK, MGL_FILL);
    gGLFT->glBindBufferARB(MGL_ELEMENT_ARRAY_BUFFER_ARB,
                           *triangles_index_buffer_handle);
    gGLFT->glDrawElements(MGL_TRIANGLES, triangles_index_buffer.size(),
                          MGL_UNSIGNED_INT, nullptr);

    gGLFT->glCullFace(silhouette_cull_face);

    // Draw Edges as Silhouettes into the color buffer.
    gGLFT->glColorMask(MGL_TRUE, MGL_TRUE, MGL_TRUE, MGL_TRUE);
    gGLFT->glPolygonMode(MGL_FRONT_AND_BACK, MGL_LINE);
    gGLFT->glBindBufferARB(MGL_ELEMENT_ARRAY_BUFFER_ARB,
                           *edge_index_buffer_handle);
    gGLFT->glDrawElements(MGL_LINES, edge_index_buffer.size(), MGL_UNSIGNED_INT,
                          nullptr);

    // Post draw, clean up
    {
        // Reset the line anti-aliasing features.
        gGLFT->glDisable(MGL_LINE_SMOOTH);
        gGLFT->glDisable(MGL_MULTISAMPLE);

        gGLFT->glDisable(MGL_CULL_FACE);
        gGLFT->glDisable(MGL_DEPTH_TEST);
        gGLFT->glDisable(MGL_POLYGON_OFFSET_FILL);

        gGLFT->glLineWidth(default_line_width);
    }

    return MS::kSuccess;
}

MStatus SilhouetteRender::execute(const MHWRender::MDrawContext& drawContext) {
    MStatus status = MS::kSuccess;
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("MM Renderer SilhouetteRender: execute.");

    MUint64 object_type_exclusions = drawContext.objectTypeExclusions();
    if (object_type_exclusions & MHWRender::MFrameContext::kExcludeMeshes) {
        // There is no need to draw the silhouette since all meshes
        // are meant to be hidden.
        return MS::kSuccess;
    }

    MMSOLVER_MAYA_VRB(
        "MM Renderer SilhouetteRender: m_silhouette_depth_offset: "
        << m_silhouette_depth_offset);
    MMSOLVER_MAYA_VRB("MM Renderer SilhouetteRender: m_silhouette_width: "
                      << m_silhouette_width);
    MMSOLVER_MAYA_VRB("MM Renderer SilhouetteRender: m_silhouette_color_r: "
                      << m_silhouette_color[0]);
    MMSOLVER_MAYA_VRB("MM Renderer SilhouetteRender: m_silhouette_color_g: "
                      << m_silhouette_color[1]);
    MMSOLVER_MAYA_VRB("MM Renderer SilhouetteRender: m_silhouette_color_b: "
                      << m_silhouette_color[2]);
    MMSOLVER_MAYA_VRB("MM Renderer SilhouetteRender: m_silhouette_alpha: "
                      << m_silhouette_alpha);
    MMSOLVER_MAYA_VRB("MM Renderer SilhouetteRender: m_silhouette_cull_face: "
                      << static_cast<int>(m_silhouette_cull_face));

    MHardwareRenderer* hardware_renderer_ptr = MHardwareRenderer::theRenderer();
    if (!gGLFT && hardware_renderer_ptr) {
        gGLFT = hardware_renderer_ptr->glFunctionTable();
        MMSOLVER_MAYA_VRB("MM Renderer SilhouetteRender: gGLFT: " << gGLFT);
    }
    if (!gGLFT) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer SilhouetteRender: Could not get OpenGL Function "
            "Table!");
        return MS::kFailure;
    }

    if (m_panel_name.length() == 0) {
        MMSOLVER_MAYA_ERR("MM Renderer SilhouetteRender: Invalid panel name.");
        return MS::kFailure;
    }

    if (drawContext.renderingDestination(m_panel_name) !=
        MFrameContext::k3dViewport) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer SilhouetteRender: Invalid rendering destination for "
            "panel name: \'"
            << m_panel_name.asChar() << "\'.");
        return MS::kFailure;
    }

    M3dView view;
    M3dView::getM3dViewFromModelPanel(m_panel_name, view);
    if (!M3dView::getM3dViewFromModelPanel(m_panel_name, view)) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer SilhouetteRender: Could not get M3dView for "
            "panel name: \'"
            << m_panel_name.asChar() << "\'.");
        return MS::kFailure;
    }

    if (m_shader_program == 0) {
        m_shader_program = build_shader_program(gGLFT);
    }

    const float default_line_width = drawContext.getGlobalLineWidth();

    float silhouette_color[3] = {m_silhouette_color[0], m_silhouette_color[1],
                                 m_silhouette_color[2]};
    MColor wireframe_color = MColor();

    // Extract OpenGL buffers from Maya mesh nodes, then render the
    // buffers using our own OpenGL pipeline.
    MItDag dag_iter = MItDag(MItDag::kDepthFirst, MFn::kMesh);
    for (; !dag_iter.isDone(); dag_iter.next()) {
        MObject current_item = dag_iter.currentItem();
        if (!current_item.hasFn(MFn::kMesh)) {
            continue;
        }

        MDagPath dag_path;
        status = MDagPath::getAPathTo(current_item, dag_path);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_ERR(
                "MM Renderer SilhouetteRender: Could not get MDagPath for "
                "DAG node.");
            continue;
        }
        if (!dag_path.isValid() || !dag_path.isVisible()) {
            continue;
        }

        if (!m_silhouette_override_color) {
            // TODO: Write our own version of
            // 'MGeometryUtilities::wireframeColor', that will do the same
            // logic, but will not take into account the current selection
            // status of the DagPath. This would avoid the need to save
            // the selection list, de-select and re-select.
            wireframe_color =
                MHWRender::MGeometryUtilities::wireframeColor(dag_path);
            silhouette_color[0] = wireframe_color.r;
            silhouette_color[1] = wireframe_color.g;
            silhouette_color[2] = wireframe_color.b;
        }

        // TODO: Check if an attribute exists on the shape node, and
        // check the value of the shape node.

        MMatrix projection_matrix = drawContext.getMatrix(
            MHWRender::MFrameContext::kProjectionMtx, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        MMatrix model_view_projection;
        status = calculate_model_view_projection_matrix(
            view, dag_path, projection_matrix, model_view_projection);

        // Create vertex buffer desc for position
        const MString empty_string = "";
        MVertexBufferDescriptor position_description = MVertexBufferDescriptor(
            empty_string, MHWRender::MGeometry::kPosition,
            MHWRender::MGeometry::kFloat, 3);
        MIndexBufferDescriptor edge_description = MIndexBufferDescriptor(
            MIndexBufferDescriptor::kEdgeLine, empty_string,
            MHWRender::MGeometry::kLines, 2);
        MIndexBufferDescriptor triangle_description = MIndexBufferDescriptor(
            MIndexBufferDescriptor::kTriangle, empty_string,
            MHWRender::MGeometry::kTriangles, 2);

        // Describes the type of data we need to get from the
        // MGeometryExtractor.
        MGeometryRequirements geometry_requirements;
        geometry_requirements.addVertexRequirement(position_description);
        geometry_requirements.addIndexingRequirement(edge_description);

        MHWRender::MPolyGeomOptions extractor_options =
            MHWRender::kPolyGeom_BaseMesh;
        MGeometryExtractor geometry_extractor = MGeometryExtractor(
            geometry_requirements, dag_path, extractor_options);

        // Create vertex and index buffers
        MVertexBuffer vertex_buffer = MVertexBuffer(position_description);
        MIndexBuffer edge_index_buffer =
            MIndexBuffer(MHWRender::MGeometry::kUnsignedInt32);
        MIndexBuffer triangles_index_buffer =
            MIndexBuffer(MHWRender::MGeometry::kUnsignedInt32);

        // Fill vertex buffer with data
        unsigned int vertex_count = geometry_extractor.vertexCount();
        void* vertices_ptr = vertex_buffer.acquire(vertex_count, true);
        geometry_extractor.populateVertexBuffer(vertices_ptr, vertex_count,
                                                position_description);
        vertex_buffer.commit(vertices_ptr);

        // Fill edge index buffer with data
        unsigned int edge_count =
            geometry_extractor.primitiveCount(edge_description);
        void* edge_indices_ptr =
            edge_index_buffer.acquire(2 * edge_count, true);
        geometry_extractor.populateIndexBuffer(edge_indices_ptr, edge_count,
                                               edge_description);
        edge_index_buffer.commit(edge_indices_ptr);

        // Fill tri index buffer with data
        unsigned int triangles_count =
            geometry_extractor.primitiveCount(triangle_description);
        void* triangles_indices_ptr =
            triangles_index_buffer.acquire(3 * triangles_count, true);
        geometry_extractor.populateIndexBuffer(
            triangles_indices_ptr, triangles_count, triangle_description);
        triangles_index_buffer.commit(triangles_indices_ptr);

        // Buffer handles
        void* vertex_buffer_handle_ptr = vertex_buffer.resourceHandle();
        void* edge_index_buffer_handle_ptr = edge_index_buffer.resourceHandle();
        void* triangles_index_buffer_handle_ptr =
            triangles_index_buffer.resourceHandle();
        if (!vertex_buffer_handle_ptr || !edge_index_buffer_handle_ptr ||
            !triangles_index_buffer_handle_ptr) {
            MMSOLVER_MAYA_ERR(
                "MM Renderer SilhouetteRender: Vertex, Edge, or Triangle "
                "OpenGL buffer objects is not valid.");
            continue;
        }

        const MGLuint* vertex_buffer_handle =
            static_cast<MGLuint*>(vertex_buffer_handle_ptr);
        const MGLuint* edge_index_buffer_handle =
            static_cast<MGLuint*>(edge_index_buffer_handle_ptr);
        const MGLuint* triangles_index_buffer_handle =
            static_cast<MGLuint*>(triangles_index_buffer_handle_ptr);
        draw_buffers(
            gGLFT, silhouette_color, m_silhouette_alpha, m_silhouette_width,
            m_silhouette_depth_offset, m_silhouette_cull_face,
            default_line_width, model_view_projection, vertex_buffer_handle,
            edge_index_buffer_handle, triangles_index_buffer_handle,
            edge_index_buffer, triangles_index_buffer, m_shader_program);
    }

    return MS::kSuccess;
}

MHWRender::MRenderTarget* const* SilhouetteRender::targetOverrideList(
    unsigned int& listSize) {
    if (m_output_targets) {
        listSize = 2;
        return &m_output_targets[0];
    }
    return nullptr;
}

}  // namespace render
}  // namespace mmsolver
