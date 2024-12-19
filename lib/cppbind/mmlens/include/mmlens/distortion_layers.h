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

#ifndef MM_LENS_DISTORTION_LAYERS_H
#define MM_LENS_DISTORTION_LAYERS_H

#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmlens {

class DistortionLayers {
public:
    MMLENS_API_EXPORT
    DistortionLayers() noexcept;

    MMLENS_API_EXPORT
    explicit DistortionLayers(rust::Box<ShimDistortionLayers> &&value) noexcept;

    MMLENS_API_EXPORT
    rust::Box<ShimDistortionLayers> get_inner() noexcept;

    MMLENS_API_EXPORT
    void set_inner(rust::Box<ShimDistortionLayers> &value) noexcept;

    MMLENS_API_EXPORT
    bool is_static() noexcept;

    MMLENS_API_EXPORT
    void frame_range(FrameNumber &start_frame, FrameNumber &end_frame) noexcept;

    MMLENS_API_EXPORT
    FrameSize frame_count() noexcept;

    MMLENS_API_EXPORT
    HashValue64 frame_hash(const FrameNumber frame) noexcept;

    MMLENS_API_EXPORT
    CameraParameters camera_parameters() noexcept;

    MMLENS_API_EXPORT
    LayerSize layer_count() const noexcept;

    MMLENS_API_EXPORT
    LensModelType layer_lens_model_type(
        const LayerIndex layer_num) const noexcept;

    MMLENS_API_EXPORT
    OptionParameters3deClassic layer_lens_parameters_3de_classic(
        const LayerIndex layer_num, const FrameNumber frame) const noexcept;

    MMLENS_API_EXPORT
    OptionParameters3deRadialStdDeg4 layer_lens_parameters_3de_radial_std_deg4(
        const LayerIndex layer_num, const FrameNumber frame) const noexcept;

    MMLENS_API_EXPORT
    OptionParameters3deAnamorphicStdDeg4
    layer_lens_parameters_3de_anamorphic_std_deg4(
        const LayerIndex layer_num, const FrameNumber frame) const noexcept;

    MMLENS_API_EXPORT
    OptionParameters3deAnamorphicStdDeg4Rescaled
    layer_lens_parameters_3de_anamorphic_std_deg4_rescaled(
        const LayerIndex layer_num, const FrameNumber frame) const noexcept;

    MMLENS_API_EXPORT
    OptionParameters3deAnamorphicStdDeg6
    layer_lens_parameters_3de_anamorphic_std_deg6(
        const LayerIndex layer_num, const FrameNumber frame) const noexcept;

    MMLENS_API_EXPORT
    OptionParameters3deAnamorphicStdDeg6Rescaled
    layer_lens_parameters_3de_anamorphic_std_deg6_rescaled(
        const LayerIndex layer_num, const FrameNumber frame) const noexcept;

    MMLENS_API_EXPORT
    rust::String as_string() noexcept;

private:
    rust::Box<ShimDistortionLayers> inner_;
};

MMLENS_API_EXPORT
DistortionLayers read_lens_file(rust::Str file_path) noexcept;

}  // namespace mmlens

#endif  // MM_LENS_DISTORTION_LAYERS_H
