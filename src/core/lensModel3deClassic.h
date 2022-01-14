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
#include <core/lensModel.h>

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
            : m_k1(0.0)
            , m_k2(0.0)
            , m_squeeze(1.0) {
        m_lensPlugin =
            std::unique_ptr<LensPluginBase>(new LensPlugin());
    };

    LensModel3deClassic(double k1, double k2, double squeeze)
            : m_k1(k1)
            , m_k2(k2)
            , m_squeeze(squeeze) {
        m_lensPlugin =
            std::unique_ptr<LensPluginBase>(new LensPlugin());
    };

    double getK1() const;
    double getK2() const;
    double getSqueeze() const;
    
    void setK1(double value);
    void setK2(double value);
    void setSqueeze(double value);

    LensModel* getInputLensModel() const;

    void setInputLensModel(LensModel* value);

    virtual void applyModel(double x,
                            double y,
                            double &out_x,
                            double &out_y) const;

private:

    LensModel* m_inputLensModel;
    std::unique_ptr<LensPluginBase> m_lensPlugin;
    double m_k1;
    double m_k2;
    double m_squeeze;
};


#endif // MAYA_MM_SOLVER_CORE_LENS_MODEL_3DE_CLASSIC_H
