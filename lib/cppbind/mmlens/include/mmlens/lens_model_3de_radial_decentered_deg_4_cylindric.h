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
 * Class for the 3DE Radial (Decentered) Degree 4 Cylindric Lens
 * Distortion.
 */

#ifndef MM_LENS_LENS_MODEL_3DE_RADIAL_DECENTERED_DEG_4_CYLINDRIC_H
#define MM_LENS_LENS_MODEL_3DE_RADIAL_DECENTERED_DEG_4_CYLINDRIC_H

// Do not define 'min' and 'max' macros on MS Windows (with MSVC),
// added to fix errors with LDPK.
#define NOMINMAX

#include <mmcore/mmhash.h>
#include <mmlens/_cxxbridge.h>
#include <mmlens/lib.h>

#include <algorithm>
#include <memory>

#include "lens_model.h"

namespace mmlens {

class LensModel3deRadialDecenteredDeg4Cylindric : public LensModel {
public:
    LensModel3deRadialDecenteredDeg4Cylindric()
        : LensModel{LensModelType::k3deRadialStdDeg4}
        , m_lens{0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0} {}

    std::unique_ptr<LensModel> cloneAsUniquePtr() const override {
        return std::unique_ptr<LensModel>(
            new LensModel3deRadialDecenteredDeg4Cylindric(*this));
    }

    std::shared_ptr<LensModel> cloneAsSharedPtr() const override {
        return std::shared_ptr<LensModel>(
            new LensModel3deRadialDecenteredDeg4Cylindric(*this));
    }

    double getDegree2Distortion() const { return m_lens.degree2_distortion; }
    double getDegree2U() const { return m_lens.degree2_u; }
    double getDegree2V() const { return m_lens.degree2_v; }
    double getDegree4Distortion() const { return m_lens.degree4_distortion; }
    double getDegree4U() const { return m_lens.degree4_u; }
    double getDegree4V() const { return m_lens.degree4_v; }
    double getCylindricDirection() const { return m_lens.cylindric_direction; }
    double getCylindricBending() const { return m_lens.cylindric_bending; }

    void setDegree2Distortion(const double value) {
        setParameter(m_lens.degree2_distortion, value);
    }

    void setDegree2U(const double value) {
        setParameter(m_lens.degree2_u, value);
    }

    void setDegree2V(const double value) {
        setParameter(m_lens.degree2_v, value);
    }

    void setDegree4Distortion(const double value) {
        setParameter(m_lens.degree4_distortion, value);
    }

    void setDegree4U(const double value) {
        setParameter(m_lens.degree4_u, value);
    }

    void setDegree4V(const double value) {
        setParameter(m_lens.degree4_v, value);
    }

    void setCylindricDirection(const double value) {
        setParameter(m_lens.cylindric_direction, value);
    }

    void setCylindricBending(const double value) {
        setParameter(m_lens.cylindric_bending, value);
    }

    void applyModelUndistort(const double x, const double y, double &out_x,
                             double &out_y) override;

    void applyModelDistort(const double x, const double y, double &out_x,
                           double &out_y) override;

    mmhash::HashValue hashValue() override;

private:
    Parameters3deRadialStdDeg4 m_lens;
};

}  // namespace mmlens

#endif  // MM_LENS_LENS_MODEL_3DE_RADIAL_DECENTERED_DEG_4_CYLINDRIC_H
