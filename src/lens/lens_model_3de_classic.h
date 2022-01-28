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

#ifndef MAYA_MM_SOLVER_CORE_LENS_MODEL_3DE_CLASSIC_H
#define MAYA_MM_SOLVER_CORE_LENS_MODEL_3DE_CLASSIC_H

// STL
#include <memory>

// Internal
#include "lens/lens_model.h"

// For loading DLLs at runtime on Unix (and there is a compatiblity
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

using LensPluginBase = tde4_ld_plugin;
using LensPlugin = tde4_ldp_classic_3de_mixed<ldpk::vec2d, ldpk::mat2d>;

class LensModel3deClassic : public LensModel {
public:

    LensModel3deClassic()
            : m_distortion(0.0)
            , m_anamorphicSqueeze(1.0)
            , m_curvatureX(0.0)
            , m_curvatureY(0.0)
            , m_quarticDistortion(0.0) {
        m_lensPlugin =
            std::unique_ptr<LensPluginBase>(new LensPlugin());
    };

    LensModel3deClassic(double distortion,
                        double anamorphic_squeeze,
                        double curvature_x,
                        double curvature_y,
                        double quartic_distortion)
            : m_distortion(distortion)
            , m_anamorphicSqueeze(anamorphic_squeeze)
            , m_curvatureX(curvature_x)
            , m_curvatureY(curvature_y)
            , m_quarticDistortion(quartic_distortion){
        m_lensPlugin = std::unique_ptr<LensPluginBase>(new LensPlugin());
    };

    double getDistortion() const;
    double getAnamorphicSqueeze() const;
    double getCurvatureX() const;
    double getCurvatureY() const;
    double getQuarticDistortion() const;

    void setDistortion(double value);
    void setAnamorphicSqueeze(double value);
    void setCurvatureX(double value);
    void setCurvatureY(double value);
    void setQuarticDistortion(double value);

    LensModel* getInputLensModel() const;

    void setInputLensModel(LensModel* value);

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


#endif // MAYA_MM_SOLVER_CORE_LENS_MODEL_3DE_CLASSIC_H
