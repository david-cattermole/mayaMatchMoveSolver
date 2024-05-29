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

#ifndef MM_SOLVER_RENDER_SHADER_SHADER_UTILS_H
#define MM_SOLVER_RENDER_SHADER_SHADER_UTILS_H

// Maya
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

namespace mmsolver {
namespace render {

const MHWRender::MShaderManager *get_shader_manager();

MString find_shader_file_path(const MString &shader_file_name);

MString read_shader_file(const MString &shader_file_path);

MHWRender::MShaderInstance *compile_shader_file(const MString &shader_file_name,
                                                const MString &technique_name);

MHWRender::MShaderInstance *compile_shader_text(const MString &shader_text,
                                                const MString &technique_name);

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_SHADER_SHADER_UTILS_H
