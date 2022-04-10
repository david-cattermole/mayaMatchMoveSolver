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
 * Class for the 3DE classic lens distortion model.
 */

#ifndef MM_SOLVER_CORE_LENS_MODEL_3DE_CLASSIC_H
#define MM_SOLVER_CORE_LENS_MODEL_3DE_CLASSIC_H

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
#pragma warning( push )

#pragma warning( disable : 4201 )
#pragma warning( disable : 4459 )
#pragma warning( disable : 4100 )

#include <ldpk/ldpk.h>
#include <ldpk/tde4_ld_plugin.h>
#include <ldpk/tde4_ldp_classic_3de_mixed.h>

#pragma warning( pop )

// MM Solver
#include "lens_model.h"

using LensPluginBase = tde4_ld_plugin;
using LensPlugin = tde4_ldp_classic_3de_mixed<ldpk::vec2d, ldpk::mat2d>;

class LensModel3deClassic : public LensModel {
public:

    LensModel3deClassic()
            : LensModel{LensModelType::k3deClassic}
            , m_distortion(0.0)
            , m_anamorphicSqueeze(1.0)
            , m_curvatureX(0.0)
            , m_curvatureY(0.0)
            , m_quarticDistortion(0.0)
            , m_lensPlugin(std::unique_ptr<LensPluginBase>(new LensPlugin()))
        {}

    LensModel3deClassic(const double distortion,
                        const double anamorphic_squeeze,
                        const double curvature_x,
                        const double curvature_y,
                        const double quartic_distortion)
            : LensModel{LensModelType::k3deClassic}
            , m_distortion(distortion)
            , m_anamorphicSqueeze(anamorphic_squeeze)
            , m_curvatureX(curvature_x)
            , m_curvatureY(curvature_y)
            , m_quarticDistortion(quartic_distortion)
            , m_lensPlugin(std::unique_ptr<LensPluginBase>(new LensPlugin()))
        {}

    LensModel3deClassic(const LensModel3deClassic &rhs)
            : LensModel{rhs}
            , m_distortion(rhs.getDistortion())
            , m_anamorphicSqueeze(rhs.getAnamorphicSqueeze())
            , m_curvatureX(rhs.getCurvatureX())
            , m_curvatureY(rhs.getCurvatureY())
            , m_quarticDistortion(rhs.getQuarticDistortion())
            , m_lensPlugin{std::unique_ptr<LensPluginBase>(new LensPlugin())}
        {}

    std::unique_ptr<LensModel>
    cloneAsUniquePtr() const override {
        return std::unique_ptr<LensModel>(new LensModel3deClassic(*this));
    }

    std::shared_ptr<LensModel>
    cloneAsSharedPtr() const override {
        return std::shared_ptr<LensModel>(new LensModel3deClassic(*this));
    }

    double getDistortion() const {return m_distortion;}
    double getAnamorphicSqueeze() const {return m_anamorphicSqueeze;}
    double getCurvatureX() const {return m_curvatureX;}
    double getCurvatureY() const {return m_curvatureY;}
    double getQuarticDistortion() const {return m_quarticDistortion;}

    void setDistortion(const double value) {
        bool same_value = m_distortion == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_distortion = value;
        }
    }

    void setAnamorphicSqueeze(const double value) {
        bool same_value = m_anamorphicSqueeze == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_anamorphicSqueeze = value;
        }
    }

    void setCurvatureX(const double value) {
        bool same_value = m_curvatureX == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_curvatureX = value;
        }
    }

    void setCurvatureY(const double value) {
        bool same_value = m_curvatureY == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_curvatureY = value;
        }
    }

    void setQuarticDistortion(const double value) {
        bool same_value = m_quarticDistortion == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_quarticDistortion = value;
        }
    }

    virtual void applyModelUndistort(
        const double x,
        const double y,
        double &out_x,
        double &out_y) const;

    virtual void applyModelDistort(
        const double x,
        const double y,
        double &out_x,
        double &out_y) const;

private:
    std::unique_ptr<LensPluginBase> m_lensPlugin;

    double m_distortion;
    double m_anamorphicSqueeze;
    double m_curvatureX;
    double m_curvatureY;
    double m_quarticDistortion;
};


#endif // MM_SOLVER_CORE_LENS_MODEL_3DE_CLASSIC_H
