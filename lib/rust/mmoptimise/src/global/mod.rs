//
// Copyright (C) 2025, 2026 David Cattermole.
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

mod caching_evaluator;
mod differential_evolution;
mod evaluator;
mod least_squares_evaluator;
mod uniform_grid_search;

pub use caching_evaluator::CachingEvaluator;
pub use differential_evolution::{
    DifferentialEvolution, DifferentialEvolutionConfig,
    DifferentialEvolutionError, DifferentialEvolutionStrategy,
    DifferentialEvolutionWorkspace,
};
pub use evaluator::Evaluator;
pub use least_squares_evaluator::LeastSquaresEvaluator;
pub use uniform_grid_search::{
    UniformGridSearch, UniformGridSearchConfig, UniformGridSearchError,
};
