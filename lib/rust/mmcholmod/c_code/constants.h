// Copyright (C) 2025 David Cattermole.
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

#pragma once

#include <inttypes.h>

// Exit codes.
#define SUCCESSFUL_EXIT 0
#define ERROR_NULL_POINTER 100000
#define ERROR_MALLOC 200000
#define ERROR_NOT_POSITIVE_DEFINITE 300000
#define ERROR_NOT_INITIALIZED 400000
#define ERROR_NOT_FACTORIZED 500000
#define ERROR_ALREADY_INITIALIZED 600000
#define ERROR_INVALID_INPUT 700000

// Boolean type.
#define C_TRUE 1
#define C_FALSE 0
#define C_BOOL int32_t

