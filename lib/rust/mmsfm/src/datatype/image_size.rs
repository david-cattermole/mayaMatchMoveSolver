//
// Copyright (C) 2025, 2026 David Cattermole.
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

//! Image size data type for pixel dimensions with aspect ratio support.

use std::fmt;

use crate::datatype::common::UnitValue;
use crate::datatype::pixel_value::PixelValue;

/// Image size representing pixel dimensions with pixel aspect ratio.
///
/// This struct represents the dimensions of an image in pixels, along with
/// the pixel aspect ratio. The pixel aspect ratio defines the horizontal
/// scaling of pixels, where a value of 2.0 means each pixel is twice as wide
/// as it is tall. This is important for SfM reconstruction where non-square
/// pixels affect the actual image aspect ratio.
///
/// # Examples
///
/// ```rust
/// use mmsfm_rust::datatype::*;
///
/// // HD image with square pixels
/// let hd_square = ImageSize::new(
///     PixelValue::new(1920.0),
///     PixelValue::new(1080.0),
///     1.0
/// );
/// assert_eq!(hd_square.aspect_ratio(), 1920.0 / 1080.0);
///
/// // HD image with anamorphic pixels (2:1 pixel aspect)
/// let hd_anamorphic = ImageSize::new(
///     PixelValue::new(1920.0),
///     PixelValue::new(1080.0),
///     2.0
/// );
/// assert_eq!(hd_anamorphic.aspect_ratio(), (1920.0 * 2.0) / 1080.0);
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct ImageSize<T> {
    /// Width of the image in pixels
    pub width: PixelValue<T>,
    /// Height of the image in pixels
    pub height: PixelValue<T>,
    /// Pixel aspect ratio (horizontal scaling factor)
    /// 1.0 = square pixels, 2.0 = pixels twice as wide as tall
    pub pixel_aspect: T,
}

impl<T> ImageSize<T>
where
    T: Copy + fmt::Debug + PartialEq,
{
    /// Create a new image size with specified dimensions and pixel aspect ratio.
    ///
    /// # Arguments
    /// * `width` - Width of the image in pixels
    /// * `height` - Height of the image in pixels
    /// * `pixel_aspect` - Pixel aspect ratio (1.0 for square pixels)
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let image_size = ImageSize::new(
    ///     PixelValue::new(1920.0),
    ///     PixelValue::new(1080.0),
    ///     1.0
    /// );
    /// assert_eq!(image_size.width.value(), 1920.0);
    /// assert_eq!(image_size.height.value(), 1080.0);
    /// assert_eq!(image_size.pixel_aspect, 1.0);
    /// ```
    pub fn new(
        width: PixelValue<T>,
        height: PixelValue<T>,
        pixel_aspect: T,
    ) -> Self {
        Self {
            width,
            height,
            pixel_aspect,
        }
    }

    /// Create a new image size from raw pixel values with square pixels.
    ///
    /// # Arguments
    /// * `width_px` - Width of the image in pixels
    /// * `height_px` - Height of the image in pixels
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let image_size = ImageSize::from_pixels(1920.0, 1080.0);
    /// assert_eq!(image_size.width.value(), 1920.0);
    /// assert_eq!(image_size.height.value(), 1080.0);
    /// assert_eq!(image_size.pixel_aspect, 1.0);
    /// ```
    pub fn from_pixels(width_px: T, height_px: T) -> Self
    where
        T: From<f64>,
    {
        Self {
            width: PixelValue::new(width_px),
            height: PixelValue::new(height_px),
            pixel_aspect: T::from(1.0),
        }
    }

    /// Create a new image size from raw pixel values with custom pixel aspect ratio.
    ///
    /// # Arguments
    /// * `width_px` - Width of the image in pixels
    /// * `height_px` - Height of the image in pixels
    /// * `pixel_aspect` - Pixel aspect ratio
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let image_size = ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0);
    /// assert_eq!(image_size.width.value(), 1920.0);
    /// assert_eq!(image_size.height.value(), 1080.0);
    /// assert_eq!(image_size.pixel_aspect, 2.0);
    /// ```
    pub fn from_pixels_with_aspect(
        width_px: T,
        height_px: T,
        pixel_aspect: T,
    ) -> Self {
        Self {
            width: PixelValue::new(width_px),
            height: PixelValue::new(height_px),
            pixel_aspect,
        }
    }
}

impl<T> ImageSize<T>
where
    T: Copy
        + std::ops::Mul<Output = T>
        + std::ops::Div<Output = T>
        + fmt::Debug
        + PartialEq,
{
    /// Calculate the aspect ratio including pixel aspect ratio.
    ///
    /// This calculates the actual displayed aspect ratio of the image,
    /// taking into account both the pixel dimensions and the pixel aspect ratio.
    ///
    /// # Returns
    /// Aspect ratio as (width * pixel_aspect) / height
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// // Square pixels: 1920x1080 = 16:9 = 1.777...
    /// let hd_square = ImageSize::from_pixels(1920.0, 1080.0);
    /// assert_eq!(hd_square.aspect_ratio(), 1920.0 / 1080.0);
    ///
    /// // Anamorphic pixels: 1920x1080 with 2.0 pixel aspect = 32:9 = 3.555...
    /// let hd_anamorphic = ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0);
    /// assert_eq!(hd_anamorphic.aspect_ratio(), (1920.0 * 2.0) / 1080.0);
    /// ```
    pub fn aspect_ratio(&self) -> T {
        (self.width.value() * self.pixel_aspect) / self.height.value()
    }

    /// Get the effective width including pixel aspect ratio.
    ///
    /// # Returns
    /// Effective width as width * pixel_aspect
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let image_size = ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0);
    /// assert_eq!(image_size.effective_width(), 3840.0);
    /// ```
    pub fn effective_width(&self) -> T {
        self.width.value() * self.pixel_aspect
    }
}

impl ImageSize<f64> {
    /// Create common image size presets.

    /// Full HD (1920x1080) with square pixels.
    pub fn full_hd() -> ImageSize<f64> {
        ImageSize::from_pixels(1920.0, 1080.0)
    }

    /// 4K UHD (3840x2160) with square pixels.
    pub fn uhd_4k() -> ImageSize<f64> {
        ImageSize::from_pixels(3840.0, 2160.0)
    }

    /// HD (1280x720) with square pixels.
    pub fn hd_720p() -> ImageSize<f64> {
        ImageSize::from_pixels(1280.0, 720.0)
    }

    /// Cinema 4K (4096x2160) with square pixels.
    pub fn cinema_4k() -> ImageSize<f64> {
        ImageSize::from_pixels(4096.0, 2160.0)
    }

    /// PAL standard definition (720x576) with square pixels.
    pub fn pal_sd() -> ImageSize<f64> {
        ImageSize::from_pixels(720.0, 576.0)
    }

    /// NTSC standard definition (720x480) with square pixels.
    pub fn ntsc_sd() -> ImageSize<f64> {
        ImageSize::from_pixels(720.0, 480.0)
    }
}

impl<T> fmt::Display for ImageSize<T>
where
    T: fmt::Display + Copy + fmt::Debug + PartialEq + From<f64>,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.pixel_aspect == T::from(1.0) {
            write!(f, "{}x{} px", self.width, self.height)
        } else {
            write!(
                f,
                "{}x{} px (PAR: {})",
                self.width, self.height, self.pixel_aspect
            )
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_image_size_creation() {
        let image_size = ImageSize::new(
            PixelValue::new(1920.0),
            PixelValue::new(1080.0),
            1.0,
        );
        assert_eq!(image_size.width.value(), 1920.0);
        assert_eq!(image_size.height.value(), 1080.0);
        assert_eq!(image_size.pixel_aspect, 1.0);
    }

    #[test]
    fn test_image_size_from_pixels() {
        let image_size = ImageSize::from_pixels(1920.0, 1080.0);
        assert_eq!(image_size.width.value(), 1920.0);
        assert_eq!(image_size.height.value(), 1080.0);
        assert_eq!(image_size.pixel_aspect, 1.0);
    }

    #[test]
    fn test_image_size_from_pixels_with_aspect() {
        let image_size =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0);
        assert_eq!(image_size.width.value(), 1920.0);
        assert_eq!(image_size.height.value(), 1080.0);
        assert_eq!(image_size.pixel_aspect, 2.0);
    }

    #[test]
    fn test_image_size_aspect_ratio() {
        // Square pixels
        let hd_square = ImageSize::from_pixels(1920.0, 1080.0);
        assert_relative_eq!(
            hd_square.aspect_ratio(),
            1920.0 / 1080.0,
            epsilon = 1e-10
        );

        // Anamorphic pixels (2:1)
        let hd_anamorphic =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0);
        assert_relative_eq!(
            hd_anamorphic.aspect_ratio(),
            (1920.0 * 2.0) / 1080.0,
            epsilon = 1e-10
        );

        // Square image with square pixels
        let square = ImageSize::from_pixels(1024.0, 1024.0);
        assert_relative_eq!(square.aspect_ratio(), 1.0, epsilon = 1e-10);

        // Square image with anamorphic pixels
        let square_anamorphic =
            ImageSize::from_pixels_with_aspect(1024.0, 1024.0, 1.5);
        assert_relative_eq!(
            square_anamorphic.aspect_ratio(),
            1.5,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_image_size_effective_width() {
        let image_size =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0);
        assert_relative_eq!(
            image_size.effective_width(),
            3840.0,
            epsilon = 1e-10
        );

        let square_pixels = ImageSize::from_pixels(1920.0, 1080.0);
        assert_relative_eq!(
            square_pixels.effective_width(),
            1920.0,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_image_size_presets() {
        // Test Full HD preset
        let full_hd = ImageSize::full_hd();
        assert_eq!(full_hd.width.value(), 1920.0);
        assert_eq!(full_hd.height.value(), 1080.0);
        assert_eq!(full_hd.pixel_aspect, 1.0);
        assert_relative_eq!(
            full_hd.aspect_ratio(),
            16.0 / 9.0,
            epsilon = 1e-10
        );

        // Test 4K UHD preset
        let uhd_4k = ImageSize::uhd_4k();
        assert_eq!(uhd_4k.width.value(), 3840.0);
        assert_eq!(uhd_4k.height.value(), 2160.0);
        assert_relative_eq!(uhd_4k.aspect_ratio(), 16.0 / 9.0, epsilon = 1e-10);

        // Test HD 720p preset
        let hd_720p = ImageSize::hd_720p();
        assert_eq!(hd_720p.width.value(), 1280.0);
        assert_eq!(hd_720p.height.value(), 720.0);
        assert_relative_eq!(
            hd_720p.aspect_ratio(),
            16.0 / 9.0,
            epsilon = 1e-10
        );

        // Test Cinema 4K preset
        let cinema_4k = ImageSize::cinema_4k();
        assert_eq!(cinema_4k.width.value(), 4096.0);
        assert_eq!(cinema_4k.height.value(), 2160.0);
        assert_relative_eq!(
            cinema_4k.aspect_ratio(),
            4096.0 / 2160.0,
            epsilon = 1e-10
        );

        // Test PAL SD preset
        let pal_sd = ImageSize::pal_sd();
        assert_eq!(pal_sd.width.value(), 720.0);
        assert_eq!(pal_sd.height.value(), 576.0);

        // Test NTSC SD preset
        let ntsc_sd = ImageSize::ntsc_sd();
        assert_eq!(ntsc_sd.width.value(), 720.0);
        assert_eq!(ntsc_sd.height.value(), 480.0);
    }

    #[test]
    fn test_image_size_equality() {
        let image_size_a =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 1.0);
        let image_size_b =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 1.0);
        let image_size_c =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0);

        assert_eq!(image_size_a, image_size_b);
        assert_ne!(image_size_a, image_size_c);
    }

    #[test]
    fn test_image_size_display() {
        let square_pixels = ImageSize::from_pixels(1920.0, 1080.0);
        assert_eq!(format!("{}", square_pixels), "1920x1080 px");

        let anamorphic_pixels =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0);
        assert_eq!(format!("{}", anamorphic_pixels), "1920x1080 px (PAR: 2)");
    }

    #[test]
    fn test_image_size_debug() {
        let image_size =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 1.5);
        let debug_str = format!("{:?}", image_size);
        assert!(debug_str.contains("1920"));
        assert!(debug_str.contains("1080"));
        assert!(debug_str.contains("1.5"));
    }

    #[test]
    fn test_image_size_with_different_numeric_types() {
        // Test with f32
        let image_size_f32 =
            ImageSize::from_pixels_with_aspect(1920.0_f32, 1080.0_f32, 2.0_f32);
        assert_relative_eq!(
            image_size_f32.aspect_ratio(),
            (1920.0_f32 * 2.0_f32) / 1080.0_f32,
            epsilon = 1e-6
        );

        // Test with f64
        let image_size_f64 =
            ImageSize::from_pixels_with_aspect(1920.0_f64, 1080.0_f64, 2.0_f64);
        assert_relative_eq!(
            image_size_f64.aspect_ratio(),
            (1920.0_f64 * 2.0_f64) / 1080.0_f64,
            epsilon = 1e-10
        );

        // Test with integers
        let image_size_int = ImageSize::from_pixels_with_aspect(1920, 1080, 2);
        assert_eq!(image_size_int.aspect_ratio(), (1920 * 2) / 1080);
    }

    #[test]
    fn test_image_size_real_world_scenarios() {
        // Test common anamorphic scenarios
        let anamorphic_2_39 =
            ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 1.33);
        assert_relative_eq!(
            anamorphic_2_39.aspect_ratio(),
            (1920.0 * 1.33) / 1080.0,
            epsilon = 1e-10
        );

        // Test DV/PAL scenario (non-square pixels)
        let dv_pal =
            ImageSize::from_pixels_with_aspect(720.0, 576.0, 16.0 / 15.0);
        assert_relative_eq!(
            dv_pal.aspect_ratio(),
            (720.0 * 16.0 / 15.0) / 576.0,
            epsilon = 1e-10
        );

        // Test DV/NTSC scenario (non-square pixels)
        let dv_ntsc =
            ImageSize::from_pixels_with_aspect(720.0, 480.0, 10.0 / 11.0);
        assert_relative_eq!(
            dv_ntsc.aspect_ratio(),
            (720.0 * 10.0 / 11.0) / 480.0,
            epsilon = 1e-10
        );
    }
}
