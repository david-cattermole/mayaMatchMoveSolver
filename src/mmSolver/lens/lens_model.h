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
#include <memory>

enum class LensModelType {
    kUninitialized = 0,
    kBasic = 1,
    k3deClassic = 2,
    kNumLensModelType,
};


class LensModel {
public:

    virtual ~LensModel() = 0;

    LensModel(LensModelType type)
            : m_type(type)
            , m_focalLength_cm(3.0)
            , m_filmBackWidth_cm(3.6)
            , m_filmBackHeight_cm(2.4)
            , m_pixelAspect(1.0)
            , m_lensCenterOffsetX_cm(0.0)
            , m_lensCenterOffsetY_cm(0.0)
            , m_inputLensModel{}
        {};

    LensModel(const LensModel &rhs)
            : m_type(rhs.getType())
            , m_focalLength_cm(rhs.getFocalLength())
            , m_filmBackWidth_cm(rhs.getFilmBackWidth())
            , m_filmBackHeight_cm(rhs.getFilmBackHeight())
            , m_pixelAspect(rhs.getPixelAspect())
            , m_lensCenterOffsetX_cm(rhs.getLensCenterOffsetX())
            , m_lensCenterOffsetY_cm(rhs.getLensCenterOffsetY())
            , m_inputLensModel{rhs.getInputLensModel()}
        {};


    virtual std::unique_ptr<LensModel> cloneAsUniquePtr() const = 0;
    virtual std::shared_ptr<LensModel> cloneAsSharedPtr() const = 0;

    LensModelType getType() const {return m_type;}
    double getFocalLength() const {return m_focalLength_cm;}
    double getFilmBackWidth() const {return m_filmBackWidth_cm;}
    double getFilmBackHeight() const {return m_filmBackHeight_cm;}
    double getPixelAspect() const {return m_pixelAspect;}
    double getLensCenterOffsetX() const {return m_lensCenterOffsetX_cm;}
    double getLensCenterOffsetY() const {return m_lensCenterOffsetY_cm;}

    void setType(const LensModelType value) {m_type = value;}
    void setFocalLength(const double value) {m_focalLength_cm = value;}
    void setFilmBackWidth(const double value) {m_filmBackWidth_cm = value;}
    void setFilmBackHeight(const double value) {m_filmBackHeight_cm = value;}
    void setPixelAspect(const double value) {m_pixelAspect = value;}
    void setLensCenterOffsetX(const double value) {m_lensCenterOffsetX_cm = value;}
    void setLensCenterOffsetY(const double value) {m_lensCenterOffsetY_cm = value;}

    std::shared_ptr<LensModel> getInputLensModel() const {return m_inputLensModel;}
    void setInputLensModel(std::shared_ptr<LensModel> value) {m_inputLensModel = value;}

    // TODO: Remove need for an explicit 'initModel' call by keeping a
    // 'state' of the lens model. Each time a value is changed, the
    // 'state' will be updated to 'dirty', and the class is
    // responsible for keeping the state and up-to-date with the lens
    // model used. For 3DE LDPK the dirty state indicates the lens
    // plug must be initialized, but for other models no such
    // requirement is needed.
    virtual void initModel() const = 0;

    virtual void applyModelUndistort(
        const double x,
        const double y,
        double &out_x,
        double &out_y) const = 0;

protected:
    std::shared_ptr<LensModel> m_inputLensModel;
    LensModelType m_type;

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
