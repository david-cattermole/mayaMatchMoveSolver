/*
 * Copyright (C) 2020 David Cattermole.
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
 * Functor class for the basic brownian lens distortion model.
 */

#ifndef MM_SOLVER_CORE_LENS_MODEL_BASIC_H
#define MM_SOLVER_CORE_LENS_MODEL_BASIC_H

#include "lens_model.h"

class LensModelBasic : public LensModel {
public:

    LensModelBasic()
            : LensModel{}
            , m_k1(0.0)
            , m_k2(0.0) {};

    LensModelBasic(const double k1,
                   const double k2)
            : LensModel{}
            , m_k1(k1)
            , m_k2(k2) {};

    double getK1() const;
    double getK2() const;

    void setK1(const double value);
    void setK2(const double value);

    void setInputLensModel(LensModel* value);

    virtual void initModel() const;

    virtual void applyModel(const double x,
                            const double y,
                            double &out_x,
                            double &out_y) const;

private:

    LensModel* m_inputLensModel;
    double m_k1;
    double m_k2;
};


#endif // MM_SOLVER_CORE_LENS_MODEL_BASIC_H
