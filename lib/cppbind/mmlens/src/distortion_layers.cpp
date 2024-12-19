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

#include <mmlens/distortion_layers.h>
#include <mmlens/lib.h>

#include <iostream>
#include <string>

namespace mmlens {

DistortionLayers::DistortionLayers() noexcept
    : inner_(shim_create_distortion_layers_box()) {}

DistortionLayers::DistortionLayers(
    rust::Box<ShimDistortionLayers> &&value) noexcept
    : inner_(std::move(value)) {}

rust::Box<ShimDistortionLayers> DistortionLayers::get_inner() noexcept {
    return std::move(inner_);
}

void DistortionLayers::set_inner(
    rust::Box<ShimDistortionLayers> &value) noexcept {
    inner_ = std::move(value);
    return;
}

bool DistortionLayers::is_static() noexcept { return inner_->is_static(); }

void DistortionLayers::frame_range(FrameNumber &start_frame,
                                   FrameNumber &end_frame) noexcept {
    inner_->frame_range(start_frame, end_frame);
}

FrameSize DistortionLayers::frame_count() noexcept {
    return inner_->frame_count();
}

HashValue64 DistortionLayers::frame_hash(const FrameNumber frame) noexcept {
    return inner_->frame_hash(frame);
}

CameraParameters DistortionLayers::camera_parameters() noexcept {
    return inner_->camera_parameters();
}

LayerSize DistortionLayers::layer_count() const noexcept {
    return inner_->layer_count();
}

LensModelType DistortionLayers::layer_lens_model_type(
    const LayerIndex layer_num) const noexcept {
    return inner_->layer_lens_model_type(layer_num);
}

OptionParameters3deClassic DistortionLayers::layer_lens_parameters_3de_classic(
    const LayerIndex layer_num, const FrameNumber frame) const noexcept {
    return inner_->layer_lens_parameters_3de_classic(layer_num, frame);
}

OptionParameters3deRadialStdDeg4
DistortionLayers::layer_lens_parameters_3de_radial_std_deg4(
    const LayerIndex layer_num, const FrameNumber frame) const noexcept {
    return inner_->layer_lens_parameters_3de_radial_std_deg4(layer_num, frame);
}

OptionParameters3deAnamorphicStdDeg4
DistortionLayers::layer_lens_parameters_3de_anamorphic_std_deg4(
    const LayerIndex layer_num, const FrameNumber frame) const noexcept {
    return inner_->layer_lens_parameters_3de_anamorphic_std_deg4(layer_num,
                                                                 frame);
}

OptionParameters3deAnamorphicStdDeg4Rescaled
DistortionLayers::layer_lens_parameters_3de_anamorphic_std_deg4_rescaled(
    const LayerIndex layer_num, const FrameNumber frame) const noexcept {
    return inner_->layer_lens_parameters_3de_anamorphic_std_deg4_rescaled(
        layer_num, frame);
}

OptionParameters3deAnamorphicStdDeg6
DistortionLayers::layer_lens_parameters_3de_anamorphic_std_deg6(
    const LayerIndex layer_num, const FrameNumber frame) const noexcept {
    return inner_->layer_lens_parameters_3de_anamorphic_std_deg6(layer_num,
                                                                 frame);
}

OptionParameters3deAnamorphicStdDeg6Rescaled
DistortionLayers::layer_lens_parameters_3de_anamorphic_std_deg6_rescaled(
    const LayerIndex layer_num, const FrameNumber frame) const noexcept {
    return inner_->layer_lens_parameters_3de_anamorphic_std_deg6_rescaled(
        layer_num, frame);
}

rust::String DistortionLayers::as_string() noexcept {
    return inner_->as_string();
}

DistortionLayers read_lens_file(rust::Str file_path) noexcept {
    return DistortionLayers(std::move(shim_read_lens_file(file_path)));
}

}  // namespace mmlens
