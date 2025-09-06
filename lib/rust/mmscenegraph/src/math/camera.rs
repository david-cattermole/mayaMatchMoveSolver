//
// Copyright (C) 2020, 2021 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// mmSolver is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
// ====================================================================
//
/// Pin-hole camera mathematics.
use nalgebra as na;

use crate::constant::Matrix44;
use crate::constant::Real;
use crate::constant::DEGREES_TO_RADIANS;
use crate::constant::INCH_TO_MM;
use crate::constant::MM_TO_CM;
use crate::constant::RADIANS_TO_DEGREES;

#[repr(u8)]
#[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
pub enum FilmFit {
    Fill = 0,
    Horizontal = 1,
    Vertical = 2,
    Overscan = 3,
}

#[derive(Debug)]
pub struct FilmFitScale {
    x: Real,
    y: Real,
}

#[derive(Debug)]
pub struct Frustum {
    right: Real,
    left: Real,
    top: Real,
    bottom: Real,
}

#[derive(Debug)]
pub struct Screen {
    size_x_mm: Real,
    size_y_mm: Real,
    right: Real,
    left: Real,
    top: Real,
    bottom: Real,
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    const EPSILON: Real = 1.0e-5;

    #[test]
    fn test_get_angle_of_view_as_degree() {
        let fbk_w = 36.0;
        let focal = 35.0;
        let aov = get_angle_of_view_as_degree(fbk_w, focal);
        assert_relative_eq!(aov, 54.432228, epsilon = EPSILON);
    }

    #[test]
    fn test_get_projection_matrix() {
        let focal_length_mm = 35.0;
        let film_back_width_inch = 36.0 / 25.4;
        let film_back_height_inch = 24.0 / 25.4;
        let film_offset_x = 0.0;
        let film_offset_y = 0.0;
        let image_width = 2048.0;
        let image_height = 1556.0;
        let film_fit = FilmFit::Horizontal;
        // This value *must* be exactly 0.1 for the maths to correct.
        let near_clip_plane_cm = 0.1;
        let far_clip_plane_cm = 10000.0;
        let camera_scale = 1.0;
        let camera_projection_matrix = get_projection_matrix(
            focal_length_mm,
            film_back_width_inch,
            film_back_height_inch,
            film_offset_x,
            film_offset_y,
            image_width,
            image_height,
            film_fit,
            near_clip_plane_cm,
            far_clip_plane_cm,
            camera_scale,
        );
        println!("Camera Projection Matrix: {}", camera_projection_matrix);

        let expected_result = na::Matrix4::<Real>::new(
            1.94445, 0.0, 0.0, 0.0, //
            0.0, 2.55927, 0.0, 0.0, //
            0.0, 0.0, 1.00002, -1.0, //
            0.0, 0.0, 0.200002, 0.0, //
        )
        .transpose();
        let eq = camera_projection_matrix.relative_eq(
            &expected_result,
            EPSILON,
            EPSILON,
        );
        assert_eq!(eq, true);
    }
}

#[inline]
pub fn get_angle_of_view_as_radian(
    film_back_size_mm: Real,
    focal_length_mm: Real,
) -> Real {
    // println!("Get Angle of View as radian");
    let angle_of_view = film_back_size_mm * (0.5 / focal_length_mm);
    2.0 * angle_of_view.atan()
}

#[inline]
pub fn get_angle_of_view_as_degree(
    film_back_size_mm: Real,
    focal_length_mm: Real,
) -> Real {
    get_angle_of_view_as_radian(film_back_size_mm, focal_length_mm)
        * RADIANS_TO_DEGREES
}

#[inline]
pub fn get_camera_plane_scale(
    film_back_size_mm: Real,
    focal_length_mm: Real,
) -> Real {
    let aov = get_angle_of_view_as_degree(film_back_size_mm, focal_length_mm);
    let scale = aov * 0.5 * DEGREES_TO_RADIANS;
    scale.tan()
}

#[inline]
pub fn compute_frustum_coordinates(
    focal_length_mm: Real,       // millimetres
    film_back_width_inch: Real,  // inches
    film_back_height_inch: Real, // inches
    film_offset_x_inch: Real,    // inches
    film_offset_y_inch: Real,    // inches
    near_clip_plane_cm: Real,    // centimetres
    camera_scale: Real,
) -> Frustum {
    // Convert everything into millimetres
    let film_width_mm = film_back_width_inch * INCH_TO_MM;
    let film_height_mm = film_back_height_inch * INCH_TO_MM;
    let offset_x_mm = film_offset_x_inch * INCH_TO_MM;
    let offset_y_mm = film_offset_y_inch * INCH_TO_MM;

    let focal_to_near = (near_clip_plane_cm / focal_length_mm) * camera_scale;
    Frustum {
        right: focal_to_near * (0.5 * film_width_mm + offset_x_mm),
        left: focal_to_near * (-0.5 * film_width_mm + offset_x_mm),
        top: focal_to_near * (0.5 * film_height_mm + offset_y_mm),
        bottom: focal_to_near * (-0.5 * film_height_mm + offset_y_mm),
    }
}

/**
 * 'Film Fit' describes how fitting of the film gate and resolution gate is calculated.
 *
 * <https://www.scratchapixel.com/lessons/3d-basic-rendering/3d-viewing-pinhole-camera/implementing-virtual-pinhole-camera>
 */
#[inline]
pub fn apply_film_fit_logic(
    frustum: Frustum,
    image_aspect_ratio: Real,
    film_aspect_ratio: Real,
    film_fit: FilmFit,
) -> (FilmFitScale, Screen) {
    let mut film_fit_scale = FilmFitScale { x: 1.0, y: 1.0 };
    let mut screen = Screen {
        size_x_mm: 0.0,
        size_y_mm: 0.0,
        left: frustum.left,
        right: frustum.right,
        top: frustum.top,
        bottom: frustum.bottom,
    };

    match film_fit {
        FilmFit::Horizontal => {
            film_fit_scale.x = image_aspect_ratio / film_aspect_ratio;
            screen.size_x_mm = frustum.right - frustum.left;
            screen.size_y_mm = screen.size_x_mm / image_aspect_ratio;
        }
        FilmFit::Vertical => {
            film_fit_scale.x = 1.0 / (image_aspect_ratio / film_aspect_ratio);
            screen.size_y_mm = frustum.top - frustum.bottom;
            screen.size_x_mm = screen.size_y_mm * image_aspect_ratio;
        }
        FilmFit::Fill => {
            if film_aspect_ratio > image_aspect_ratio {
                film_fit_scale.x = film_aspect_ratio / image_aspect_ratio;
                screen.size_y_mm = frustum.top - frustum.bottom;
                screen.size_x_mm = screen.size_y_mm * image_aspect_ratio;
            } else {
                film_fit_scale.y = image_aspect_ratio / film_aspect_ratio;
                screen.size_x_mm = frustum.right - frustum.left;
                screen.size_y_mm = (screen.size_x_mm
                    * (film_aspect_ratio / image_aspect_ratio))
                    / film_aspect_ratio;
            }
        }
        FilmFit::Overscan => {
            if film_aspect_ratio > image_aspect_ratio {
                film_fit_scale.y = image_aspect_ratio / film_aspect_ratio;
                screen.size_x_mm = frustum.right - frustum.left;
                screen.size_y_mm =
                    (frustum.right - frustum.left) / image_aspect_ratio;
            } else {
                film_fit_scale.x = film_aspect_ratio / image_aspect_ratio;
                screen.size_x_mm = (frustum.right - frustum.left)
                    * (image_aspect_ratio / film_aspect_ratio);
                screen.size_y_mm = frustum.top - frustum.bottom;
            }
        }
    }
    screen.right *= film_fit_scale.x;
    screen.left *= film_fit_scale.x;
    screen.top *= film_fit_scale.y;
    screen.bottom *= film_fit_scale.y;
    (film_fit_scale, screen)
}

#[inline]
pub fn compute_projection_matrix(
    film_fit_scale: FilmFitScale,
    screen: Screen,
    near_clip_plane_cm: Real,
    far_clip_plane_cm: Real,
    _camera_scale: Real,
) -> Matrix44 {
    // println!("Compute Projection Matrix");
    na::Matrix4::<Real>::new(
        // First Row
        1.0 / (screen.size_x_mm * 0.5) * MM_TO_CM,
        0.0,
        0.0,
        0.0,
        // Second Row
        0.0,
        1.0 / (screen.size_y_mm * 0.5) * MM_TO_CM,
        0.0,
        0.0,
        // Third Row
        (screen.right + screen.left) / (screen.right - screen.left)
            * film_fit_scale.x,
        (screen.top + screen.bottom) / (screen.top - screen.bottom)
            * film_fit_scale.y,
        (far_clip_plane_cm + near_clip_plane_cm)
            / (far_clip_plane_cm - near_clip_plane_cm),
        2.0 * far_clip_plane_cm * near_clip_plane_cm
            / (far_clip_plane_cm - near_clip_plane_cm),
        // Forth Row
        0.0,
        0.0,
        -1.0,
        0.0,
    )
}

#[inline]
pub fn get_projection_matrix(
    focal_length_mm: Real,
    film_back_width_inch: Real,
    film_back_height_inch: Real,
    film_offset_x_inch: Real,
    film_offset_y_inch: Real,
    image_width_pixels: Real,
    image_height_pixels: Real,
    film_fit: FilmFit,
    near_clip_plane_cm: Real,
    far_clip_plane_cm: Real,
    camera_scale: Real,
) -> Matrix44 {
    // println!("Get Projection Matrix: {}in x {}in by {}mm", film_back_width_inch, film_back_height_inch, focal_length_mm);
    // println!("near_clip_plane_cm: {}cm", near_clip_plane_cm);
    // println!("far_clip_plane_cm: {}cm", far_clip_plane_cm);

    let film_aspect_ratio: Real = film_back_width_inch / film_back_height_inch;
    let image_aspect_ratio: Real = image_width_pixels / image_height_pixels;
    let frustum = compute_frustum_coordinates(
        focal_length_mm,
        film_back_width_inch,
        film_back_height_inch,
        film_offset_x_inch,
        film_offset_y_inch,
        near_clip_plane_cm,
        camera_scale,
    );

    // Apply 'Film Fit'
    let (film_fit_scale, screen) = apply_film_fit_logic(
        frustum,
        image_aspect_ratio,
        film_aspect_ratio,
        film_fit,
    );

    // Projection Matrix
    compute_projection_matrix(
        film_fit_scale,
        screen,
        near_clip_plane_cm,
        far_clip_plane_cm,
        camera_scale,
    )
}
