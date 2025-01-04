/*
 * Copyright (C) 2023 David Cattermole.
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

#include "shader_utils.h"

// STL
#include <fstream>
#include <string>

// Maya
#include <maya/M3dView.h>
#include <maya/MGlobal.h>
#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/path_utils.h"

namespace mmsolver {
namespace render {

const MHWRender::MShaderManager *get_shader_manager() {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_ERR("MM Renderer: failed to get renderer.");
        return nullptr;
    }

    const MHWRender::MShaderManager *shader_manager =
        renderer->getShaderManager();
    if (!shader_manager) {
        MMSOLVER_MAYA_ERR("MM Renderer failed get shader manager.");
        return nullptr;
    }

    if (renderer->drawAPI() == MHWRender::kOpenGLCoreProfile) {
        // In core profile, there used to be the problem where the shader
        // fails to load sometimes.  The problem occurs when the OpenGL
        // Device Context is switched before calling the
        // GLSLShaderNode::loadEffect() function(this switch is performed
        // by Tmodel::selectManip).  When that occurs, the shader is
        // loaded in the wrong context instead of the viewport
        // context... so that in the draw phase, after switching to the
        // viewport context, the drawing is erroneous.  In order to solve
        // that problem, make the view context current
        MStatus status = MS::kSuccess;
        M3dView view = M3dView::active3dView(&status);
        if (status != MStatus::kSuccess) {
            MMSOLVER_MAYA_ERR("MM Renderer: Could not set active view.");
            return nullptr;
        }
        view.makeSharedContextCurrent();
    }
    return shader_manager;
}

MString find_shader_file_path(const MString &shader_file_name) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB("MM Renderer finding shader file..."
                      << " shader_file_name=" << shader_file_name.asChar());

    MString shader_file_path = "";
    const MHWRender::MShaderManager *shader_manager = get_shader_manager();
    if (!shader_manager) {
        return shader_file_path;
    }

    MStringArray shader_paths;
    MStatus status = shader_manager->shaderPaths(shader_paths);
    if (status != MStatus::kSuccess) {
        return shader_file_path;
    }

    for (auto i = 0; i < shader_paths.length(); i++) {
        MMSOLVER_MAYA_VRB("MM Renderer look for shader in: "
                          << " shader_paths[" << i
                          << "]=" << shader_paths[i].asChar());

        MString test_file_path = shader_paths[i];
        const auto found_forward_slash_index = test_file_path.rindex('/');
        MMSOLVER_MAYA_VRB(
            "MM Renderer test_file_path.length(): " << test_file_path.length());
        MMSOLVER_MAYA_VRB("MM Renderer found_forward_slash_index: "
                          << found_forward_slash_index);
        if (found_forward_slash_index != (test_file_path.length() - 1)) {
            test_file_path += MString("/");
        }
        test_file_path += shader_file_name;
        // TODO: Should we automatically try and find the file name
        // with the '.ogsfx' appended?
        MMSOLVER_MAYA_VRB(
            "MM Renderer test_file_path: " << test_file_path.asChar());

        status = mmpath::resolve_input_file_path(test_file_path);
        if ((status == MStatus::kSuccess) && (test_file_path.length() > 0)) {
            shader_file_path = test_file_path;
            break;
        }
    }

    return shader_file_path;
}

MString read_shader_file(const MString &shader_file_path) {
    std::ifstream file_stream(shader_file_path.asChar());
    const std::string content((std::istreambuf_iterator<char>(file_stream)),
                              (std::istreambuf_iterator<char>()));
    return MString(content.c_str());
}

MHWRender::MShaderInstance *compile_shader_file(const MString &shader_file_name,
                                                const MString &technique_name) {
    const bool verbose = false;
    MStatus status = MS::kSuccess;

    MMSOLVER_MAYA_VRB("MM Renderer compiling shader file..."
                      << " shader_file_name=" << shader_file_name.asChar()
                      << " technique_name=" << technique_name.asChar());

    const MHWRender::MShaderManager *shader_manager = get_shader_manager();
    if (!shader_manager) {
        return nullptr;
    }

    // Shader compiling options.
    MShaderCompileMacro *macros = nullptr;
    const unsigned int number_of_macros = 0;
    const bool use_effect_cache = true;

    // Get Techniques.
    MMSOLVER_MAYA_VRB("MM Renderer: Get techniques...");
    MStringArray technique_names;
    shader_manager->getEffectsTechniques(shader_file_name, technique_names,
                                         macros, number_of_macros,
                                         use_effect_cache);
    for (uint32_t i = 0; i < technique_names.length(); ++i) {
        MMSOLVER_MAYA_VRB("MM Renderer: technique"
                          << i << ": " << technique_names[i].asChar());
    }
    if (technique_names.length() == 0) {
        MMSOLVER_MAYA_ERR("MM Renderer: shader contains no techniques.");
        return nullptr;
    }

    // Compile shader.
    MMSOLVER_MAYA_VRB("MM Renderer: Compiling shader...");
    MHWRender::MShaderInstance *shader_instance =
        shader_manager->getEffectsFileShader(shader_file_name, technique_name,
                                             macros, number_of_macros,
                                             use_effect_cache);
    if (!shader_instance) {
        MString error_message =
            MString("MM Renderer failed to compile shader.");
        bool display_line_number = true;
        bool filter_source = true;
        uint32_t num_lines = 3;

        const MString last_error = MHWRender::MShaderManager::getLastError();
        const MString last_error_source =
            MHWRender::MShaderManager::getLastErrorSource(
                display_line_number, filter_source, num_lines);

        MGlobal::displayError(error_message);
        MGlobal::displayError(last_error);
        MGlobal::displayError(last_error_source);
        MMSOLVER_MAYA_ERR("MM Renderer failed to compile shader.");
        MMSOLVER_MAYA_ERR(last_error.asChar());
        MMSOLVER_MAYA_ERR(last_error_source);
        return nullptr;
    }

    MStringArray parameter_list;
    shader_instance->parameterList(parameter_list);
    for (uint32_t i = 0; i < parameter_list.length(); ++i) {
        MMSOLVER_MAYA_VRB("MM Renderer: param " << i << ": "
                                                << parameter_list[i].asChar());
    }

    return shader_instance;
}

MHWRender::MShaderInstance *compile_shader_text(const MString &shader_text,
                                                const MString &technique_name) {
    const bool verbose = false;
    MStatus status = MS::kSuccess;

    MMSOLVER_MAYA_VRB("MM Renderer compiling shader file..."
                      << " technique_name=" << technique_name.asChar());
    MMSOLVER_MAYA_VRB("Shader text: ");
    MMSOLVER_MAYA_VRB(shader_text.asChar());

    const MHWRender::MShaderManager *shader_manager = get_shader_manager();
    if (!shader_manager) {
        return nullptr;
    }

    const void *text_buffer = static_cast<const void *>(shader_text.asChar());
    const unsigned int text_buffer_size =
        static_cast<unsigned int>(shader_text.length());

    // Shader compiling options.
    MShaderCompileMacro *macros = nullptr;
    const unsigned int number_of_macros = 0;
    const bool use_effect_cache = true;

    // Compile shader.
    MMSOLVER_MAYA_VRB("MM Renderer: Compiling shader...");
    MHWRender::MShaderInstance *shader_instance =
        shader_manager->getEffectsBufferShader(
            text_buffer, text_buffer_size, technique_name, macros,
            number_of_macros, use_effect_cache);
    if (!shader_instance) {
        MString error_message =
            MString("MM Renderer failed to compile shader.");
        bool display_line_number = true;
        bool filter_source = true;
        uint32_t num_lines = 3;

        const MString last_error = MHWRender::MShaderManager::getLastError();
        const MString last_error_source =
            MHWRender::MShaderManager::getLastErrorSource(
                display_line_number, filter_source, num_lines);

        MGlobal::displayError(error_message);
        MGlobal::displayError(last_error);
        MGlobal::displayError(last_error_source);
        MMSOLVER_MAYA_ERR("MM Renderer failed to compile shader.");
        MMSOLVER_MAYA_ERR(last_error.asChar());
        MMSOLVER_MAYA_ERR(last_error_source.asChar());
        return nullptr;
    }

    MStringArray parameter_list;
    shader_instance->parameterList(parameter_list);
    for (uint32_t i = 0; i < parameter_list.length(); ++i) {
        MMSOLVER_MAYA_VRB("MM Renderer: param " << i << ": "
                                                << parameter_list[i].asChar());
    }

    return shader_instance;
}

}  // namespace render
}  // namespace mmsolver
