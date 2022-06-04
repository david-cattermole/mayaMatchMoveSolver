/*
 * Copyright (C) 2022 David Cattermole.
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
 * and Squeeze X/Y.
 */

#ifndef MM_SOLVER_CORE_LENS_MODEL_3DE_ANAMORPHIC_DEG_4_ROTATE_SQUEEZE_XY_H
#define MM_SOLVER_CORE_LENS_MODEL_3DE_ANAMORPHIC_DEG_4_ROTATE_SQUEEZE_XY_H

// Do not define 'min' and 'max' macros on MS Windows (with MSVC),
// added to fix errors with LDPK.
#define NOMINMAX

// STL
#include <algorithm>
#include <memory>

// For loading DLLs at runtime on Unix (and there is a compatibility
// later in 'dlfcn-win32') for Windows.
#include <dlfcn.h>

// LDPK
#pragma warning(push)

#pragma warning(disable : 4201)
#pragma warning(disable : 4459)
#pragma warning(disable : 4100)

#include <ldpk/ldpk.h>
#include <ldpk/tde4_ld_plugin.h>
#include <ldpk/tde4_ldp_anamorphic_deg_4_rotate_squeeze_xy.h>

#pragma warning(pop)

// MM Solver
#include "lens_model.h"
#include "mmSolver/core/mmhash.h"

using LensPluginBase = tde4_ld_plugin;
using LensPluginAnamorphicDeg4RotateSqueezeXY =
    tde4_ldp_anamorphic_deg_4_rotate_squeeze_xy<ldpk::vec2d, ldpk::mat2d>;

class LensModel3deAnamorphicDeg4RotateSqueezeXY : public LensModel {
public:
    LensModel3deAnamorphicDeg4RotateSqueezeXY()
        : LensModel{LensModelType::k3deAnamorphicDeg4}
        , m_degree2_cx02(0.0)
        , m_degree2_cy02(0.0)
        , m_degree2_cx22(0.0)
        , m_degree2_cy22(0.0)
        , m_degree4_cx04(0.0)
        , m_degree4_cy04(0.0)
        , m_degree4_cx24(0.0)
        , m_degree4_cy24(0.0)
        , m_degree4_cx44(0.0)
        , m_degree4_cy44(0.0)
        , m_lensRotation(0.0)
        , m_squeeze_x(1.0)
        , m_squeeze_y(1.0)
        , m_lensPlugin(std::unique_ptr<LensPluginBase>(
              new LensPluginAnamorphicDeg4RotateSqueezeXY())) {}

    LensModel3deAnamorphicDeg4RotateSqueezeXY(
        const double degree2_cx02, const double degree2_cy02,
        const double degree2_cx22, const double degree2_cy22,
        const double degree4_cx04, const double degree4_cy04,
        const double degree4_cx24, const double degree4_cy24,
        const double degree4_cx44, const double degree4_cy44,
        const double lensRotation, const double squeeze_x,
        const double squeeze_y)
        : LensModel{LensModelType::k3deAnamorphicDeg4}
        , m_degree2_cx02(degree2_cx02)
        , m_degree2_cy02(degree2_cy02)
        , m_degree2_cx22(degree2_cx22)
        , m_degree2_cy22(degree2_cy22)
        , m_degree4_cx04(degree4_cx04)
        , m_degree4_cy04(degree4_cy04)
        , m_degree4_cx24(degree4_cx24)
        , m_degree4_cy24(degree4_cy24)
        , m_degree4_cx44(degree4_cx44)
        , m_degree4_cy44(degree4_cy44)
        , m_lensRotation(lensRotation)
        , m_squeeze_x(squeeze_x)
        , m_squeeze_y(squeeze_y)
        , m_lensPlugin(std::unique_ptr<LensPluginBase>(
              new LensPluginAnamorphicDeg4RotateSqueezeXY())) {}

    LensModel3deAnamorphicDeg4RotateSqueezeXY(
        const LensModel3deAnamorphicDeg4RotateSqueezeXY &rhs)
        : LensModel{rhs}
        , m_degree2_cx02(rhs.getDegree2Cx02())
        , m_degree2_cy02(rhs.getDegree2Cy02())
        , m_degree2_cx22(rhs.getDegree2Cx22())
        , m_degree2_cy22(rhs.getDegree2Cy22())
        , m_degree4_cx04(rhs.getDegree4Cx04())
        , m_degree4_cy04(rhs.getDegree4Cy04())
        , m_degree4_cx24(rhs.getDegree4Cx24())
        , m_degree4_cy24(rhs.getDegree4Cy24())
        , m_degree4_cx44(rhs.getDegree4Cx44())
        , m_degree4_cy44(rhs.getDegree4Cy44())
        , m_lensRotation(rhs.getLensRotation())
        , m_squeeze_x(rhs.getSqueezeX())
        , m_squeeze_y(rhs.getSqueezeY())
        , m_lensPlugin{std::unique_ptr<LensPluginBase>(
              new LensPluginAnamorphicDeg4RotateSqueezeXY())} {}

    std::unique_ptr<LensModel> cloneAsUniquePtr() const override {
        return std::unique_ptr<LensModel>(
            new LensModel3deAnamorphicDeg4RotateSqueezeXY(*this));
    }

    std::shared_ptr<LensModel> cloneAsSharedPtr() const override {
        return std::shared_ptr<LensModel>(
            new LensModel3deAnamorphicDeg4RotateSqueezeXY(*this));
    }

    double getDegree2Cx02() const { return m_degree2_cx02; }
    double getDegree2Cy02() const { return m_degree2_cy02; }

    double getDegree2Cx22() const { return m_degree2_cx22; }
    double getDegree2Cy22() const { return m_degree2_cy22; }

    double getDegree4Cx04() const { return m_degree4_cx04; }
    double getDegree4Cy04() const { return m_degree4_cy04; }

    double getDegree4Cx24() const { return m_degree4_cx24; }
    double getDegree4Cy24() const { return m_degree4_cy24; }

    double getDegree4Cx44() const { return m_degree4_cx44; }
    double getDegree4Cy44() const { return m_degree4_cy44; }

    double getLensRotation() const { return m_lensRotation; }
    double getSqueezeX() const { return m_squeeze_x; }
    double getSqueezeY() const { return m_squeeze_y; }

    void setDegree2Cx02(const double value) {
        bool same_value = m_degree2_cx02 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree2_cx02 = value;
        }
    }

    void setDegree2Cy02(const double value) {
        bool same_value = m_degree2_cy02 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree2_cy02 = value;
        }
    }

    void setDegree2Cx22(const double value) {
        bool same_value = m_degree2_cx22 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree2_cx22 = value;
        }
    }

    void setDegree2Cy22(const double value) {
        bool same_value = m_degree2_cy22 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree2_cy22 = value;
        }
    }

    void setDegree4Cx04(const double value) {
        bool same_value = m_degree4_cx04 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_cx04 = value;
        }
    }

    void setDegree4Cy04(const double value) {
        bool same_value = m_degree4_cy04 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_cy04 = value;
        }
    }

    void setDegree4Cx24(const double value) {
        bool same_value = m_degree4_cx24 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_cx24 = value;
        }
    }

    void setDegree4Cy24(const double value) {
        bool same_value = m_degree4_cy24 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_cy24 = value;
        }
    }

    void setDegree4Cx44(const double value) {
        bool same_value = m_degree4_cx44 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_cx44 = value;
        }
    }

    void setDegree4Cy44(const double value) {
        bool same_value = m_degree4_cy44 == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_cy44 = value;
        }
    }

    void setLensRotation(const double value) {
        bool same_value = m_lensRotation == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lensRotation = value;
        }
    }

    void setSqueezeX(const double value) {
        bool same_value = m_squeeze_x == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_squeeze_x = value;
        }
    }

    void setSqueezeY(const double value) {
        bool same_value = m_squeeze_y == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_squeeze_y = value;
        }
    }

    virtual void applyModelUndistort(const double x, const double y,
                                     double &out_x, double &out_y);

    virtual void applyModelDistort(const double x, const double y,
                                   double &out_x, double &out_y);

    virtual mmhash::HashValue hashValue();

private:
    std::unique_ptr<LensPluginBase> m_lensPlugin;

    double m_degree2_cx02;  // "Cx02 - Degree 2"
    double m_degree2_cy02;  // "Cy02 - Degree 2"

    double m_degree2_cx22;  // "Cx22 - Degree 2"
    double m_degree2_cy22;  // "Cy22 - Degree 2"

    double m_degree4_cx04;  // "Cx04 - Degree 4"
    double m_degree4_cy04;  // "Cy04 - Degree 4"

    double m_degree4_cx24;  // "Cx24 - Degree 4"
    double m_degree4_cy24;  // "Cy24 - Degree 4"

    double m_degree4_cx44;  // "Cx44 - Degree 4"
    double m_degree4_cy44;  // "Cy44 - Degree 4"

    double m_lensRotation;  // "Lens Rotation"
    double m_squeeze_x;     // "Squeeze-X"
    double m_squeeze_y;     // "Squeeze-Y"
};

#endif  // MM_SOLVER_CORE_LENS_MODEL_3DE_ANAMORPHIC_DEG_4_ROTATE_SQUEEZE_XY_H
