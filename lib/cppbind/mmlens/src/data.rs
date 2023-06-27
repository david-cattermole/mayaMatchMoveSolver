//
// Copyright (C) 2023 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// mmSolver is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
// ====================================================================
//

use crate::constants::MAX_LENS_PARAMETER_COUNT;

/// Frame numbers 0 to 65534 are valid.
///
/// Frame number 65535 is reserved to indicate a static value
/// (STATIC_FRAME_NUMBER).
///
/// It's assumed that frame numbers less than 0 do not make much sense
/// since the produced file name would be invalid because it has a
/// minus sign '-' at the start.
pub type FrameNumber = u16;
pub type FrameSize = u16;

pub type ParameterBlock = [f64; MAX_LENS_PARAMETER_COUNT];
pub type ParameterIndex = u32;
pub type ParameterSize = u8;

pub type LayerIndex = u8;
pub type LayerSize = u8;

pub type HashValue64 = u64;
