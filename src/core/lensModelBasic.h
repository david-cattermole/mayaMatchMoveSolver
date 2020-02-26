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
 * Fanctor class for the basic brownian lens distortion model.
 */

#ifndef MAYA_MM_SOLVER_CORE_LENS_MODEL_BASIC_H
#define MAYA_MM_SOLVER_CORE_LENS_MODEL_BASIC_H

#include <core/lensModel.h>

class LensModelBasic : public LensModel {
public:

    LensModelBasic() : k1(0.0), k2(0.0) {};

    virtual void applyModel(double x,
                            double y,
                            double &out_x,
                            double &out_y) const;

private:

    double k1;
    double k2;
};


#endif // MAYA_MM_SOLVER_CORE_LENS_MODEL_BASIC_H
