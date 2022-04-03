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

#ifndef MM_SOLVER_CORE_LENS_MODEL_H
#define MM_SOLVER_CORE_LENS_MODEL_H

// STL
// #include <vector>
#include <memory>

class LensModel {
public:

    virtual ~LensModel() = 0;

    LensModel()
            : m_focalLength_cm(3.0)
            , m_filmBackWidth_cm(3.6)
            , m_filmBackHeight_cm(2.4)
            , m_pixelAspect(1.0)
            , m_lensCenterOffsetX_cm(0.0)
            , m_lensCenterOffsetY_cm(0.0)
        {};

    LensModel(const LensModel &rhs)
            : m_focalLength_cm(rhs.getFocalLength())
            , m_filmBackWidth_cm(rhs.getFilmBackWidth())
            , m_filmBackHeight_cm(rhs.getFilmBackHeight())
            , m_pixelAspect(rhs.getPixelAspect())
            , m_lensCenterOffsetX_cm(rhs.getLensCenterOffsetX())
            , m_lensCenterOffsetY_cm(rhs.getLensCenterOffsetY())
        {};

    virtual std::unique_ptr<LensModel> clone() const = 0;

    double getFocalLength() const {return m_focalLength_cm;}
    double getFilmBackWidth() const {return m_filmBackWidth_cm;}
    double getFilmBackHeight() const {return m_filmBackHeight_cm;}
    double getPixelAspect() const {return m_pixelAspect;}
    double getLensCenterOffsetX() const {return m_lensCenterOffsetX_cm;}
    double getLensCenterOffsetY() const {return m_lensCenterOffsetY_cm;}

    void setFocalLength(const double value) {m_focalLength_cm = value;}
    void setFilmBackWidth(const double value) {m_filmBackWidth_cm = value;}
    void setFilmBackHeight(const double value) {m_filmBackHeight_cm = value;}
    void setPixelAspect(const double value) {m_pixelAspect = value;}
    void setLensCenterOffsetX(const double value) {m_lensCenterOffsetX_cm = value;}
    void setLensCenterOffsetY(const double value) {m_lensCenterOffsetY_cm = value;}

    virtual void initModel() const = 0;
    virtual void applyModel(const double x,
                            const double y,
                            double &out_x,
                            double &out_y) const = 0;

protected:
    // cm = centimeter, the unit of the value.
    double m_focalLength_cm;
    double m_filmBackWidth_cm;
    double m_filmBackHeight_cm;
    double m_pixelAspect;
    double m_lensCenterOffsetX_cm;
    double m_lensCenterOffsetY_cm;
};


inline LensModel::~LensModel() {}





#endif // MM_SOLVER_CORE_LENS_MODEL_H
