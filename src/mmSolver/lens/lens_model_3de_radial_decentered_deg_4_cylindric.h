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
 * Class for the 3DE Radial (Decentered) Degree 4 Cylindric Lens
 * Distortion.
 */

#ifndef MM_SOLVER_CORE_LENS_MODEL_3DE_RADIAL_DECENTERED_DEG_4_CYLINDRIC_H
#define MM_SOLVER_CORE_LENS_MODEL_3DE_RADIAL_DECENTERED_DEG_4_CYLINDRIC_H

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
#include <ldpk/tde4_ldp_radial_decentered_deg_4_cylindric.h>

#pragma warning( pop )

// MM Solver
#include "lens_model.h"
#include "mmSolver/core/mmhash.h"

using LensPluginBase = tde4_ld_plugin;
using LensPluginRadialDecenteredDeg4Cylindric =
        tde4_ldp_radial_decentered_deg_4_cylindric<ldpk::vec2d, ldpk::mat2d>;

class LensModel3deRadialDecenteredDeg4Cylindric : public LensModel {
public:

    LensModel3deRadialDecenteredDeg4Cylindric()
            : LensModel{LensModelType::k3deRadialDeg4}
            , m_degree2_distortion(0.0)
            , m_degree2_u(0.0)
            , m_degree2_v(0.0)
            , m_degree4_distortion(0.0)
            , m_degree4_u(0.0)
            , m_degree4_v(0.0)
            , m_cylindricDirection(0.0)
            , m_cylindricBending(0.0)
            , m_lensPlugin(std::unique_ptr<LensPluginBase>(new LensPluginRadialDecenteredDeg4Cylindric()))
        {}

    LensModel3deRadialDecenteredDeg4Cylindric(
        const double degree2_distortion,
        const double degree2_u,
        const double degree2_v,
        const double degree4_distortion,
        const double degree4_u,
        const double degree4_v,
        const double cylindricDirection,
        const double cylindricBending)
            : LensModel{LensModelType::k3deRadialDeg4}
            , m_degree2_distortion(degree2_distortion)
            , m_degree2_u(degree2_u)
            , m_degree2_v(degree2_v)
            , m_degree4_distortion(degree4_distortion)
            , m_degree4_u(degree4_u)
            , m_degree4_v(degree4_v)
            , m_cylindricDirection(cylindricDirection)
            , m_cylindricBending(cylindricBending)
            , m_lensPlugin(std::unique_ptr<LensPluginBase>(new LensPluginRadialDecenteredDeg4Cylindric()))
        {}

    LensModel3deRadialDecenteredDeg4Cylindric(
        const LensModel3deRadialDecenteredDeg4Cylindric &rhs)
            : LensModel{rhs}
            , m_degree2_distortion(rhs.getDegree2Distortion())
            , m_degree2_u(rhs.getDegree2U())
            , m_degree2_v(rhs.getDegree2V())
            , m_degree4_distortion(rhs.getDegree4Distortion())
            , m_degree4_u(rhs.getDegree4U())
            , m_degree4_v(rhs.getDegree4V())
            , m_cylindricDirection(rhs.getCylindricDirection())
            , m_cylindricBending(rhs.getCylindricBending())
            , m_lensPlugin{std::unique_ptr<LensPluginBase>(new LensPluginRadialDecenteredDeg4Cylindric())}
        {}

    std::unique_ptr<LensModel>
    cloneAsUniquePtr() const override {
        return std::unique_ptr<LensModel>(new LensModel3deRadialDecenteredDeg4Cylindric(*this));
    }

    std::shared_ptr<LensModel>
    cloneAsSharedPtr() const override {
        return std::shared_ptr<LensModel>(new LensModel3deRadialDecenteredDeg4Cylindric(*this));
    }

    double getDegree2Distortion() const {return m_degree2_distortion;}
    double getDegree2U() const {return m_degree2_u;}
    double getDegree2V() const {return m_degree2_v;}
    double getDegree4Distortion() const {return m_degree4_distortion;}
    double getDegree4U() const {return m_degree4_u;}
    double getDegree4V() const {return m_degree4_v;}
    double getCylindricDirection() const {return m_cylindricDirection;}
    double getCylindricBending() const {return m_cylindricBending;}

    void setDegree2Distortion(const double value) {
        bool same_value = m_degree2_distortion == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree2_distortion = value;
        }
    }

    void setDegree2U(const double value) {
        bool same_value = m_degree2_u == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree2_u = value;
        }
    }

    void setDegree2V(const double value) {
        bool same_value = m_degree2_v == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree2_v = value;
        }
    }

    void setDegree4Distortion(const double value) {
        bool same_value = m_degree4_distortion == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_distortion = value;
        }
    }

    void setDegree4U(const double value) {
        bool same_value = m_degree4_u == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_u = value;
        }
    }

    void setDegree4V(const double value) {
        bool same_value = m_degree4_v == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_degree4_v = value;
        }
    }

    void setCylindricDirection(const double value) {
        bool same_value = m_cylindricDirection == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_cylindricDirection = value;
        }
    }

    void setCylindricBending(const double value) {
        bool same_value = m_cylindricBending == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_cylindricBending = value;
        }
    }

    virtual void applyModelUndistort(
        const double x,
        const double y,
        double &out_x,
        double &out_y);

    virtual void applyModelDistort(
        const double x,
        const double y,
        double &out_x,
        double &out_y);

    virtual mmhash::HashValue hashValue();

private:
    std::unique_ptr<LensPluginBase> m_lensPlugin;

    double m_degree2_distortion; // "Distortion - Degree 2"
    double m_degree2_u;          // "U - Degree 2"
    double m_degree2_v;          // "V - Degree 2"

    double m_degree4_distortion; // "Quartic Distortion - Degree 4"
    double m_degree4_u;          // "U - Degree 4"
    double m_degree4_v;          // "V - Degree 4"

    double m_cylindricDirection; // "Phi - Cylindric Direction"
    double m_cylindricBending;   // "B - Cylindric Bending"
};


#endif // MM_SOLVER_CORE_LENS_MODEL_3DE_RADIAL_DECENTERED_DEG_4_CYLINDRIC_H
