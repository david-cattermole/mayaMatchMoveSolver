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
 * Class for the basic brownian lens distortion model.
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
            : LensModel{}
            , m_distortion(0.0)
            , m_anamorphicSqueeze(1.0)
            , m_curvatureX(0.0)
            , m_curvatureY(0.0)
            , m_quarticDistortion(0.0) {
        m_lensPlugin =
            std::unique_ptr<LensPluginBase>(new LensPlugin());
    };

    LensModel3deClassic(const double distortion,
                        const double anamorphic_squeeze,
                        const double curvature_x,
                        const double curvature_y,
                        const double quartic_distortion)
            : LensModel{}
            , m_distortion(distortion)
            , m_anamorphicSqueeze(anamorphic_squeeze)
            , m_curvatureX(curvature_x)
            , m_curvatureY(curvature_y)
            , m_quarticDistortion(quartic_distortion){
        m_lensPlugin =
            std::unique_ptr<LensPluginBase>(new LensPlugin());
    };

    double getDistortion() const;
    double getAnamorphicSqueeze() const;
    double getCurvatureX() const;
    double getCurvatureY() const;
    double getQuarticDistortion() const;

    void setDistortion(const double value);
    void setAnamorphicSqueeze(const double value);
    void setCurvatureX(const double value);
    void setCurvatureY(const double value);
    void setQuarticDistortion(const double value);

    LensModel* getInputLensModel() const;

    void setInputLensModel(LensModel* value);

    virtual void initModel() const;

    virtual void applyModel(double x,
                            double y,
                            double &out_x,
                            double &out_y) const;

private:

    LensModel* m_inputLensModel;
    std::unique_ptr<LensPluginBase> m_lensPlugin;

    double m_distortion;
    double m_anamorphicSqueeze;
    double m_curvatureX;
    double m_curvatureY;
    double m_quarticDistortion;
};


#endif // MM_SOLVER_CORE_LENS_MODEL_3DE_CLASSIC_H
