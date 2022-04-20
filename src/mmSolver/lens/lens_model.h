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

enum class LensModelState {
    kUninitialized = 0,
    kClean = 1,
    kDirty = 2,
    kNumLensModelState,
};

// Warning: Do not change the numbers assigned to the different
// types. These numbers are exposed to the user via the
// "mmLensModel3de" node, with attribute 'lensModel'.
enum class LensModelType {
    kUninitialized = 0,

    // Does nothing but passes through to the next lens model (if
    // there is one).
    kPassthrough = 1,

    // "3DE Classic LD Model"
    k3deClassic = 2,

    // "3DE4 Radial - Standard, Degree 4"
    k3deRadialDeg4 = 3,

    // "3DE4 Anamorphic - Standard, Degree 4"
    k3deAnamorphicDeg4 = 4,

    // // "3DE4 Anamorphic - Rescaled, Degree 4"
    // k3deAnamorphicDeg4Rescaled = 5,

    // // "3DE4 Anamorphic, Degree 6"
    // k3deAnamorphicDeg6 = 6,

    kNumLensModelType,
};

class LensModel {
public:

    virtual ~LensModel() = 0;

    LensModel(LensModelType type)
            : m_type(type)
            , m_state(LensModelState::kDirty)
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
            , m_state(rhs.getState())
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
    LensModelState getState() const {return m_state;}
    double getFocalLength() const {return m_focalLength_cm;}
    double getFilmBackWidth() const {return m_filmBackWidth_cm;}
    double getFilmBackHeight() const {return m_filmBackHeight_cm;}
    double getPixelAspect() const {return m_pixelAspect;}
    double getLensCenterOffsetX() const {return m_lensCenterOffsetX_cm;}
    double getLensCenterOffsetY() const {return m_lensCenterOffsetY_cm;}

    void setType(const LensModelType value) {
        bool same_value = m_type == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_type = value;
        }
    }

    void setFocalLength(const double value) {
        bool same_value = m_focalLength_cm == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_focalLength_cm = value;
        }
    }

    void setFilmBackWidth(const double value) {
        bool same_value = m_filmBackWidth_cm == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_filmBackWidth_cm = value;
        }
    }

    void setFilmBackHeight(const double value) {
        bool same_value = m_filmBackHeight_cm == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_filmBackHeight_cm = value;
        }
    }

    void setPixelAspect(const double value) {
        bool same_value = m_pixelAspect == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_pixelAspect = value;
        }
    }

    void setLensCenterOffsetX(const double value) {
        bool same_value = m_lensCenterOffsetX_cm == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lensCenterOffsetX_cm = value;
        }
    }

    void setLensCenterOffsetY(const double value) {
        bool same_value = m_lensCenterOffsetY_cm == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_lensCenterOffsetY_cm = value;
        }
    }

    std::shared_ptr<LensModel> getInputLensModel() const {return m_inputLensModel;}
    void setInputLensModel(std::shared_ptr<LensModel> value) {
        bool same_value = m_inputLensModel == value;
        if (!same_value) {
            m_state = LensModelState::kDirty;
            m_inputLensModel = value;
        }
    }

    virtual void applyModelUndistort(
        const double x,
        const double y,
        double &out_x,
        double &out_y) = 0;

    virtual void applyModelDistort(
        const double x,
        const double y,
        double &out_x,
        double &out_y) = 0;

protected:
    std::shared_ptr<LensModel> m_inputLensModel;
    LensModelType m_type;
    LensModelState m_state;

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
