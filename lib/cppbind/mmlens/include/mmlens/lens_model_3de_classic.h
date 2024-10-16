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
 * Class for the 3DE classic lens distortion model.
 */

#ifndef MM_LENS_LENS_MODEL_3DE_CLASSIC_H
#define MM_LENS_LENS_MODEL_3DE_CLASSIC_H

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

class LensModel3deClassic : public LensModel {
public:
    LensModel3deClassic()
        : LensModel{LensModelType::k3deClassic}
        , m_lens{0.0, 1.0, 0.0, 0.0, 0.0} {};

    LensModel3deClassic(const double distortion,
                        const double anamorphic_squeeze,
                        const double curvature_x, const double curvature_y,
                        const double quartic_distortion)
        : LensModel{LensModelType::k3deClassic}
        , m_lens{distortion, anamorphic_squeeze, curvature_x, curvature_y,
                 quartic_distortion} {};

    LensModel3deClassic(const LensModel3deClassic &rhs)
        : LensModel{rhs}
        , m_lens{rhs.getDistortion(), rhs.getAnamorphicSqueeze(),
                 rhs.getCurvatureX(), rhs.getCurvatureY(),
                 rhs.getQuarticDistortion()} {};

    std::unique_ptr<LensModel> cloneAsUniquePtr() const override {
        return std::unique_ptr<LensModel>(new LensModel3deClassic(*this));
    }

    std::shared_ptr<LensModel> cloneAsSharedPtr() const override {
        return std::shared_ptr<LensModel>(new LensModel3deClassic(*this));
    }

    double getDistortion() const { return m_lens.distortion; }
    double getAnamorphicSqueeze() const { return m_lens.anamorphic_squeeze; }
    double getCurvatureX() const { return m_lens.curvature_x; }
    double getCurvatureY() const { return m_lens.curvature_y; }
    double getQuarticDistortion() const { return m_lens.quartic_distortion; }

    void setDistortion(const double value) {
        bool same_value = m_lens.distortion == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.distortion = value;
        }
    }

    void setAnamorphicSqueeze(const double value) {
        bool same_value = m_lens.anamorphic_squeeze == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.anamorphic_squeeze = value;
        }
    }

    void setCurvatureX(const double value) {
        bool same_value = m_lens.curvature_x == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.curvature_x = value;
        }
    }

    void setCurvatureY(const double value) {
        bool same_value = m_lens.curvature_y == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.curvature_y = value;
        }
    }

    void setQuarticDistortion(const double value) {
        bool same_value = m_lens.quartic_distortion == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.quartic_distortion = value;
        }
    }

    void applyModelUndistort(const double x, const double y, double &out_x,
                             double &out_y) override;

    void applyModelDistort(const double x, const double y, double &out_x,
                           double &out_y) override;

    mmhash::HashValue hashValue() override;

private:
    Parameters3deClassic m_lens;
};

}  // namespace mmlens

#endif  // MM_LENS_LENS_MODEL_3DE_CLASSIC_H
