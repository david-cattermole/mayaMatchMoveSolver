/*
 * Copyright (C) 2024 David Cattermole.
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
 * Class for the 3DE Anamorphic Degree 6 Lens Distortion with Rotation
 * and Squeeze X/Y - and 'rescaled' parameter to support images that
 * have reformated pixel aspect to 1.0.
 */

#ifndef MM_LENS_LENS_MODEL_3DE_ANAMORPHIC_DEG_6_ROTATE_SQUEEZE_XY_RESCALED_H
#define MM_LENS_LENS_MODEL_3DE_ANAMORPHIC_DEG_6_ROTATE_SQUEEZE_XY_RESCALED_H

// Do not define 'min' and 'max' macros on MS Windows (with MSVC),
// added to fix errors with LDPK.
#define NOMINMAX

#include <mmcore/mmhash.h>

#include <algorithm>
#include <memory>

#include "lens_model.h"

namespace mmlens {

class LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled : public LensModel {
public:
    LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled()
        : LensModel{LensModelType::k3deAnamorphicStdDeg6Rescaled}
        , m_lens{0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0} {}

    LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled(
        const double degree2_cx02, const double degree2_cy02,
        const double degree2_cx22, const double degree2_cy22,
        const double degree4_cx04, const double degree4_cy04,
        const double degree4_cx24, const double degree4_cy24,
        const double degree4_cx44, const double degree4_cy44,
        const double degree6_cx06, const double degree6_cy06,
        const double degree6_cx26, const double degree6_cy26,
        const double degree6_cx46, const double degree6_cy46,
        const double degree6_cx66, const double degree6_cy66,
        const double lens_rotation, const double squeeze_x,
        const double squeeze_y, const double rescale)
        : LensModel{LensModelType::k3deAnamorphicStdDeg6}
        , m_lens{degree2_cx02, degree2_cy02, degree2_cx22,  degree2_cy22,
                 degree4_cx04, degree4_cy04, degree4_cx24,  degree4_cy24,
                 degree4_cx44, degree4_cy44, degree6_cx06,  degree6_cy06,
                 degree6_cx26, degree6_cy26, degree6_cx46,  degree6_cy46,
                 degree6_cx66, degree6_cy66, lens_rotation, squeeze_x,
                 squeeze_y,    rescale} {}

    LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled(
        const LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled &rhs)
        : LensModel{rhs}
        , m_lens{
              rhs.getDegree2Cx02(),  rhs.getDegree2Cy02(), rhs.getDegree2Cx22(),
              rhs.getDegree2Cy22(),  rhs.getDegree4Cx04(), rhs.getDegree4Cy04(),
              rhs.getDegree4Cx24(),  rhs.getDegree4Cy24(), rhs.getDegree4Cx44(),
              rhs.getDegree4Cy44(),  rhs.getDegree6Cx06(), rhs.getDegree6Cy06(),
              rhs.getDegree6Cx26(),  rhs.getDegree6Cy26(), rhs.getDegree6Cx46(),
              rhs.getDegree6Cy46(),  rhs.getDegree6Cx66(), rhs.getDegree6Cy66(),
              rhs.getLensRotation(), rhs.getSqueezeX(),    rhs.getSqueezeY(),
              rhs.getRescale()} {}

    std::unique_ptr<LensModel> cloneAsUniquePtr() const override {
        return std::unique_ptr<LensModel>(
            new LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled(*this));
    }

    std::shared_ptr<LensModel> cloneAsSharedPtr() const override {
        return std::shared_ptr<LensModel>(
            new LensModel3deAnamorphicDeg6RotateSqueezeXYRescaled(*this));
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

    double getDegree6Cx06() const { return m_lens.degree6_cx06; }
    double getDegree6Cy06() const { return m_lens.degree6_cy06; }
    double getDegree6Cx26() const { return m_lens.degree6_cx26; }
    double getDegree6Cy26() const { return m_lens.degree6_cy26; }
    double getDegree6Cx46() const { return m_lens.degree6_cx46; }
    double getDegree6Cy46() const { return m_lens.degree6_cy46; }
    double getDegree6Cx66() const { return m_lens.degree6_cx66; }
    double getDegree6Cy66() const { return m_lens.degree6_cy66; }

    double getLensRotation() const { return m_lens.lens_rotation; }
    double getSqueezeX() const { return m_lens.squeeze_x; }
    double getSqueezeY() const { return m_lens.squeeze_y; }
    double getRescale() const { return m_lens.rescale; }

    void setDegree2Cx02(const double value) {
        bool same_value = m_lens.degree2_cx02 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree2_cx02 = value;
        }
    }

    void setDegree2Cy02(const double value) {
        bool same_value = m_lens.degree2_cy02 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree2_cy02 = value;
        }
    }

    void setDegree2Cx22(const double value) {
        bool same_value = m_lens.degree2_cx22 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree2_cx22 = value;
        }
    }

    void setDegree2Cy22(const double value) {
        bool same_value = m_lens.degree2_cy22 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree2_cy22 = value;
        }
    }

    void setDegree4Cx04(const double value) {
        bool same_value = m_lens.degree4_cx04 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree4_cx04 = value;
        }
    }

    void setDegree4Cy04(const double value) {
        bool same_value = m_lens.degree4_cy04 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree4_cy04 = value;
        }
    }

    void setDegree4Cx24(const double value) {
        bool same_value = m_lens.degree4_cx24 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree4_cx24 = value;
        }
    }

    void setDegree4Cy24(const double value) {
        bool same_value = m_lens.degree4_cy24 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree4_cy24 = value;
        }
    }

    void setDegree4Cx44(const double value) {
        bool same_value = m_lens.degree4_cx44 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree4_cx44 = value;
        }
    }

    void setDegree4Cy44(const double value) {
        bool same_value = m_lens.degree4_cy44 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree4_cy44 = value;
        }
    }

    void setDegree6Cx06(const double value) {
        bool same_value = m_lens.degree6_cx06 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree6_cx06 = value;
        }
    }

    void setDegree6Cy06(const double value) {
        bool same_value = m_lens.degree6_cy06 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree6_cy06 = value;
        }
    }

    void setDegree6Cx26(const double value) {
        bool same_value = m_lens.degree6_cx26 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree6_cx26 = value;
        }
    }

    void setDegree6Cy26(const double value) {
        bool same_value = m_lens.degree6_cy26 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree6_cy26 = value;
        }
    }

    void setDegree6Cx46(const double value) {
        bool same_value = m_lens.degree6_cx46 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree6_cx46 = value;
        }
    }

    void setDegree6Cy46(const double value) {
        bool same_value = m_lens.degree6_cy46 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree6_cy46 = value;
        }
    }

    void setDegree6Cx66(const double value) {
        bool same_value = m_lens.degree6_cx66 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree6_cx66 = value;
        }
    }

    void setDegree6Cy66(const double value) {
        bool same_value = m_lens.degree6_cy66 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.degree6_cy66 = value;
        }
    }

    void setLensRotation(const double value) {
        bool same_value = m_lens.lens_rotation == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.lens_rotation = value;
        }
    }

    void setSqueezeX(const double value) {
        bool same_value = m_lens.squeeze_x == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.squeeze_x = value;
        }
    }

    void setSqueezeY(const double value) {
        bool same_value = m_lens.squeeze_y == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.squeeze_y = value;
        }
    }

    void setRescale(const double value) {
        bool same_value = m_lens.rescale == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lens.rescale = value;
        }
    }

    void applyModelUndistort(const double x, const double y, double &out_x,
                             double &out_y) override;

    void applyModelDistort(const double x, const double y, double &out_x,
                           double &out_y) override;

    mmhash::HashValue hashValue() override;

private:
    Parameters3deAnamorphicStdDeg6Rescaled m_lens;
};

}  // namespace mmlens

#endif  // MM_LENS_LENS_MODEL_3DE_ANAMORPHIC_DEG_6_ROTATE_SQUEEZE_XY_RESCALED_H
