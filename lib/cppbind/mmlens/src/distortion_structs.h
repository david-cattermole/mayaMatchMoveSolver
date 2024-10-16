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
 * Wraps LDPK functions in an interface so that template code can call
 * the LDPK functions while wrapping the complexity of the different
 * LDPK/3DEqualizer lens models into easy-to-call functions.
 *
 * The assumption of using the Abstract Base Class "Distortion" is to
 * create a method contract that all classes must fulfill in order to
 * work in templates.
 */

// Must have M_PI defined before LDPK is included.
#define _USE_MATH_DEFINES
#include <math.h>

// LDPK and MM Solver
#include <ldpk/ldpk_classic_3de_mixed_distortion.h>
#include <ldpk/ldpk_cylindric_extender.h>
#include <ldpk/ldpk_generic_anamorphic_distortion.h>
#include <ldpk/ldpk_linear_extender.h>
#include <ldpk/ldpk_radial_decentered_distortion.h>
#include <ldpk/ldpk_rotation_extender.h>
#include <ldpk/ldpk_squeeze_extender.h>
#include <ldpk/ldpk_vec2d.h>
#include <mmcore/mmdata.h>
#include <mmcore/mmhash.h>

namespace mmlens {

class Distortion {
public:
    // Set parameter
    virtual void set_parameter(const int index, const double value) = 0;

    // Call this once before calling 'eval' or 'map_inverse'.
    virtual void initialize_parameters(CameraParameters camera_parameters) = 0;

    // Undistort point.
    virtual mmdata::Vector2D eval(const mmdata::Vector2D in_point_dn) const = 0;

    // Distort, without initial values.
    virtual mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn) const = 0;

    // Distort, With an initial guess.
    //
    // The guess can be used to speed up the overall calculation and
    // reduce the number of iterations, however the initial guess
    // usually requires a data structure and book-keeping for looking
    // up the initial guess values.
    virtual mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn,
        const mmdata::Vector2D in_initial_point_dn) const = 0;
};

class Distortion3deClassic : public Distortion {
public:
    Distortion3deClassic() {}

    void set_parameter(const int index, const double value) override {
        m_distortion.set_coeff(index, value);
    }

    void initialize_parameters(CameraParameters camera_parameters) override {}

    mmdata::Vector2D eval(const mmdata::Vector2D in_point_dn) const override {
        ldpk::vec2d out_point_dn =
            m_distortion.eval(ldpk::vec2d(in_point_dn.x_, in_point_dn.y_));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

    mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn) const override {
        ldpk::vec2d out_point_dn = m_distortion.map_inverse(
            ldpk::vec2d(in_point_dn.x_, in_point_dn.y_));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

    mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn,
        const mmdata::Vector2D in_initial_point_dn) const override {
        ldpk::vec2d out_point_dn = m_distortion.map_inverse(
            ldpk::vec2d(in_point_dn.x_, in_point_dn.y_),
            ldpk::vec2d(in_initial_point_dn.x_, in_initial_point_dn.y_));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

private:
    ldpk::classic_3de_mixed_distortion<ldpk::vec2d, ldpk::mat2d> m_distortion;
};

class Distortion3deRadialStdDeg4 : public Distortion {
public:
    Distortion3deRadialStdDeg4() {}

    void set_parameter(const int index, const double value) override {
        if (index < 6) {
            m_radial.set_coeff(index, value);
        } else if (index == 6) {
            m_cylindric.set_phi(value);
        } else if (index == 7) {
            m_cylindric.set_b(value);
        }
        return;
    }

    void initialize_parameters(CameraParameters camera_parameters) override {}

    mmdata::Vector2D eval(const mmdata::Vector2D in_point_dn) const override {
        ldpk::vec2d out_point_dn = m_cylindric.eval(
            m_radial.eval(ldpk::vec2d(in_point_dn.x_, in_point_dn.y_)));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

    mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn) const override {
        ldpk::vec2d out_point_dn = m_radial.map_inverse(
            m_cylindric.eval_inv(ldpk::vec2d(in_point_dn.x_, in_point_dn.y_)));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

    mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn,
        const mmdata::Vector2D in_initial_point_dn) const override {
        ldpk::vec2d out_point_dn = m_radial.map_inverse(
            m_cylindric.eval_inv(ldpk::vec2d(in_point_dn.x_, in_point_dn.y_)),
            m_cylindric.eval_inv(
                ldpk::vec2d(in_initial_point_dn.x_, in_initial_point_dn.y_)));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

private:
    ldpk::radial_decentered_distortion<ldpk::vec2d, ldpk::mat2d> m_radial;
    ldpk::cylindric_extender_2<ldpk::vec2d, ldpk::mat2d> m_cylindric;
};

class Distortion3deAnamorphicStdDeg4 : public Distortion {
public:
    Distortion3deAnamorphicStdDeg4() {}

    void set_parameter(const int index, const double value) override {
        if (index < 10) {
            m_anamorphic.set_coeff(index, value);
        } else if (index == 10) {
            m_rotation.set_phi(value / 180.0 * M_PI);
        } else if (index == 11) {
            m_squeeze_x.set_sq(value);
        } else if (index == 12) {
            m_squeeze_y.set_sq(value);
        }
        return;
    }

    void initialize_parameters(CameraParameters camera_parameters) override {
        m_pixel_aspect.set_sq(camera_parameters.pixel_aspect);
        m_rotation_squeeze_xy_pixel_aspect.set(m_rotation, m_squeeze_x,
                                               m_squeeze_y, m_pixel_aspect);

        m_pixel_aspect_and_rotation.set(m_pixel_aspect, m_rotation);

        m_anamorphic.prepare();
    }

    mmdata::Vector2D eval(const mmdata::Vector2D in_point_dn) const override {
        ldpk::vec2d out_point_dn = m_rotation_squeeze_xy_pixel_aspect.eval(
            m_anamorphic.eval(m_pixel_aspect_and_rotation.eval_inv(
                ldpk::vec2d(in_point_dn.x_, in_point_dn.y_))));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

    mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn) const override {
        ldpk::vec2d out_point_dn =
            m_pixel_aspect_and_rotation.eval(m_anamorphic.map_inverse(
                m_rotation_squeeze_xy_pixel_aspect.eval_inv(
                    ldpk::vec2d(in_point_dn.x_, in_point_dn.y_))));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

    mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn,
        const mmdata::Vector2D in_initial_point_dn) const override {
        ldpk::vec2d out_point_dn =
            m_pixel_aspect_and_rotation.eval(m_anamorphic.map_inverse(
                m_rotation_squeeze_xy_pixel_aspect.eval_inv(
                    ldpk::vec2d(in_point_dn.x_, in_point_dn.y_)),
                m_rotation_squeeze_xy_pixel_aspect.eval_inv(ldpk::vec2d(
                    in_initial_point_dn.x_, in_initial_point_dn.y_))));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

private:
    // Anamorphic distortion of degree 4.
    ldpk::generic_anamorphic_distortion<ldpk::vec2d, ldpk::mat2d, 4>
        m_anamorphic;

    // Extenders for lens rotation, squeeze and pixel aspect ratio.
    ldpk::rotation_extender<ldpk::vec2d, ldpk::mat2d> m_rotation;
    ldpk::squeeze_x_extender<ldpk::vec2d, ldpk::mat2d> m_squeeze_x;
    ldpk::squeeze_y_extender<ldpk::vec2d, ldpk::mat2d> m_squeeze_y;
    ldpk::squeeze_x_extender<ldpk::vec2d, ldpk::mat2d> m_pixel_aspect;

    // Concatenating extenders for better performance
    ldpk::linear_extender<ldpk::vec2d, ldpk::mat2d>
        m_rotation_squeeze_xy_pixel_aspect;
    ldpk::linear_extender<ldpk::vec2d, ldpk::mat2d> m_pixel_aspect_and_rotation;
};

class Distortion3deAnamorphicStdDeg4Rescaled : public Distortion {
public:
    Distortion3deAnamorphicStdDeg4Rescaled() {}

    void set_parameter(const int index, const double value) override {
        if (index < 10) {
            m_anamorphic.set_coeff(index, value);
        } else if (index == 10) {
            m_rotation.set_phi(value / 180.0 * M_PI);
        } else if (index == 11) {
            m_squeeze_x.set_sq(value);
        } else if (index == 12) {
            m_squeeze_y.set_sq(value);
        } else if (index == 13) {
            m_rescale.set_sq(value);
        }
        return;
    }

    void initialize_parameters(CameraParameters camera_parameters) override {
        m_pixel_aspect.set_sq(camera_parameters.pixel_aspect);
        m_rotation_squeeze_xy_rescale_pixel_aspect.set(
            m_rotation, m_squeeze_x, m_squeeze_y, m_rescale, m_pixel_aspect);

        m_pixel_aspect_rescale_and_rotation.set(m_pixel_aspect, m_rescale,
                                                m_rotation);

        m_anamorphic.prepare();
    }

    mmdata::Vector2D eval(const mmdata::Vector2D in_point_dn) const override {
        ldpk::vec2d out_point_dn =
            m_rotation_squeeze_xy_rescale_pixel_aspect.eval(
                m_anamorphic.eval(m_pixel_aspect_rescale_and_rotation.eval_inv(
                    ldpk::vec2d(in_point_dn.x_, in_point_dn.y_))));

        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

    mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn) const override {
        ldpk::vec2d out_point_dn =
            m_pixel_aspect_rescale_and_rotation.eval(m_anamorphic.map_inverse(
                m_rotation_squeeze_xy_rescale_pixel_aspect.eval_inv(
                    ldpk::vec2d(in_point_dn.x_, in_point_dn.y_))));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

    mmdata::Vector2D map_inverse(
        const mmdata::Vector2D in_point_dn,
        const mmdata::Vector2D in_initial_point_dn) const override {
        ldpk::vec2d out_point_dn =
            m_pixel_aspect_rescale_and_rotation.eval(m_anamorphic.map_inverse(
                m_rotation_squeeze_xy_rescale_pixel_aspect.eval_inv(
                    ldpk::vec2d(in_point_dn.x_, in_point_dn.y_)),
                m_rotation_squeeze_xy_rescale_pixel_aspect.eval_inv(ldpk::vec2d(
                    in_initial_point_dn.x_, in_initial_point_dn.y_))));
        return mmdata::Vector2D(out_point_dn[0], out_point_dn[1]);
    }

private:
    // Anamorphic distortion of degree 4.
    ldpk::generic_anamorphic_distortion<ldpk::vec2d, ldpk::mat2d, 4>
        m_anamorphic;

    // Extenders for lens rotation, squeeze and pixel aspect ratio.
    ldpk::rotation_extender<ldpk::vec2d, ldpk::mat2d> m_rotation;
    ldpk::squeeze_x_extender<ldpk::vec2d, ldpk::mat2d> m_squeeze_x;
    ldpk::squeeze_y_extender<ldpk::vec2d, ldpk::mat2d> m_squeeze_y;
    ldpk::squeeze_x_extender<ldpk::vec2d, ldpk::mat2d> m_pixel_aspect;
    ldpk::squeeze_x_extender<ldpk::vec2d, ldpk::mat2d> m_rescale;

    // Concatenating extenders for better performance
    ldpk::linear_extender<ldpk::vec2d, ldpk::mat2d>
        m_rotation_squeeze_xy_rescale_pixel_aspect;
    ldpk::linear_extender<ldpk::vec2d, ldpk::mat2d>
        m_pixel_aspect_rescale_and_rotation;
};

}  // namespace mmlens
