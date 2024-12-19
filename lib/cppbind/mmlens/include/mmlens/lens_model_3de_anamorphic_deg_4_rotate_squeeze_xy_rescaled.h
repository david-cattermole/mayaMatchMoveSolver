/*
 * Copyright (C) 2022, 2023 David Cattermole.
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
 * Class for the 3DE Anamorphic Degree 4 Lens Distortion with Rotation
 * and Squeeze X/Y - and 'rescaled' parameter to support images that
 * have reformated pixel aspect to 1.0.
 */

#ifndef MM_LENS_LENS_MODEL_3DE_ANAMORPHIC_DEG_4_ROTATE_SQUEEZE_XY_RESCALED_H
#define MM_LENS_LENS_MODEL_3DE_ANAMORPHIC_DEG_4_ROTATE_SQUEEZE_XY_RESCALED_H

// Do not define 'min' and 'max' macros on MS Windows (with MSVC),
// added to fix errors with LDPK.
#define NOMINMAX

#include <mmcore/mmhash.h>

#include <algorithm>
#include <memory>

#include "lens_model.h"

namespace mmlens {

class LensModel3deAnamorphicDeg4RotateSqueezeXYRescaled : public LensModel {
public:
    LensModel3deAnamorphicDeg4RotateSqueezeXYRescaled()
        : LensModel{LensModelType::k3deAnamorphicStdDeg4Rescaled}
        , m_lens{0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0} {}

    std::unique_ptr<LensModel> cloneAsUniquePtr() const override {
        return std::unique_ptr<LensModel>(
            new LensModel3deAnamorphicDeg4RotateSqueezeXYRescaled(*this));
    }

    std::shared_ptr<LensModel> cloneAsSharedPtr() const override {
        return std::shared_ptr<LensModel>(
            new LensModel3deAnamorphicDeg4RotateSqueezeXYRescaled(*this));
    }

    double getDegree2Cx02() const { return m_lens.degree2_cx02; }
    double getDegree2Cy02() const { return m_lens.degree2_cy02; }

    double getDegree2Cx22() const { return m_lens.degree2_cx22; }
    double getDegree2Cy22() const { return m_lens.degree2_cy22; }

    double getDegree4Cx04() const { return m_lens.degree4_cx04; }
    double getDegree4Cy04() const { return m_lens.degree4_cy04; }

    double getDegree4Cx24() const { return m_lens.degree4_cx24; }
    double getDegree4Cy24() const { return m_lens.degree4_cy24; }

    double getDegree4Cx44() const { return m_lens.degree4_cx44; }
    double getDegree4Cy44() const { return m_lens.degree4_cy44; }

    double getLensRotation() const { return m_lens.lens_rotation; }
    double getSqueezeX() const { return m_lens.squeeze_x; }
    double getSqueezeY() const { return m_lens.squeeze_y; }
    double getRescale() const { return m_lens.rescale; }

    void setDegree2Cx02(const double value) {
        setParameter(m_lens.degree2_cx02, value);
    }
    void setDegree2Cy02(const double value) {
        setParameter(m_lens.degree2_cy02, value);
    }
    void setDegree2Cx22(const double value) {
        setParameter(m_lens.degree2_cx22, value);
    }
    void setDegree2Cy22(const double value) {
        setParameter(m_lens.degree2_cy22, value);
    }

    void setDegree4Cx04(const double value) {
        setParameter(m_lens.degree4_cx04, value);
    }
    void setDegree4Cy04(const double value) {
        setParameter(m_lens.degree4_cy04, value);
    }
    void setDegree4Cx24(const double value) {
        setParameter(m_lens.degree4_cx24, value);
    }
    void setDegree4Cy24(const double value) {
        setParameter(m_lens.degree4_cy24, value);
    }
    void setDegree4Cx44(const double value) {
        setParameter(m_lens.degree4_cx44, value);
    }
    void setDegree4Cy44(const double value) {
        setParameter(m_lens.degree4_cy44, value);
    }

    void setLensRotation(const double value) {
        setParameter(m_lens.lens_rotation, value);
    }
    void setSqueezeX(const double value) {
        setParameter(m_lens.squeeze_x, value);
    }
    void setSqueezeY(const double value) {
        setParameter(m_lens.squeeze_y, value);
    }
    void setRescale(const double value) { setParameter(m_lens.rescale, value); }

    void applyModelUndistort(const double x, const double y, double &out_x,
                             double &out_y) override;

    void applyModelDistort(const double x, const double y, double &out_x,
                           double &out_y) override;

    mmhash::HashValue hashValue() override;

private:
    Parameters3deAnamorphicStdDeg4Rescaled m_lens;
};

}  // namespace mmlens

#endif  // MM_LENS_LENS_MODEL_3DE_ANAMORPHIC_DEG_4_ROTATE_SQUEEZE_XY_RESCALED_H
