/*
 * Copyright (C) 2020,2022 David Cattermole.
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
 * Class for a pass-through 'null' lens distortion model.
 */

#ifndef MM_LENS_LENS_MODEL_PASSTHROUGH_H
#define MM_LENS_LENS_MODEL_PASSTHROUGH_H

#include <mmcore/mmhash.h>

#include <memory>

#include "lens_model.h"

namespace mmlens {

class LensModelPassthrough : public LensModel {
public:
    LensModelPassthrough() : LensModel{LensModelType::kPassthrough} {}

    std::unique_ptr<LensModel> cloneAsUniquePtr() const override {
        return std::unique_ptr<LensModel>(new LensModelPassthrough(*this));
    }

    std::shared_ptr<LensModel> cloneAsSharedPtr() const override {
        return std::shared_ptr<LensModel>(new LensModelPassthrough(*this));
    }

    void applyModelUndistort(const double x, const double y, double &out_x,
                             double &out_y) override;
    void applyModelDistort(const double x, const double y, double &out_x,
                           double &out_y) override;

    mmhash::HashValue hashValue() override;
};

}  // namespace mmlens

#endif  // MM_LENS_LENS_MODEL_PASSTHROUGH_H
