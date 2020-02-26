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
 * Abstract base-class for all the LensModels.
 */

#ifndef MAYA_MM_SOLVER_CORE_LENS_MODEL_H
#define MAYA_MM_SOLVER_CORE_LENS_MODEL_H


class LensModel {
public:

    virtual ~LensModel() = 0;

    virtual void applyModel(double x,
                            double y,
                            double &out_x,
                            double &out_y) const = 0;
};


inline LensModel::~LensModel() {}


// typedef int(*FunctPtr)(...params...);

// #define LENS_MODEL_FUNC (*func)(double, double, &double &double)
// typedef void (LensModel::*MemberFunc)(double x, double y, double &out_x, double &out_y);

typedef void (LensModel::*LensModelMembFn)(double x,
                                           double y,
                                           double &out_x,
                                           double &out_y);

// Shortcut to calling a member function of a specific class.
#define CALL_MEMBER_FUNC(object, ptr_to_member) ((object).*(ptrToMember))


#endif // MAYA_MM_SOLVER_CORE_LENS_MODEL_H
