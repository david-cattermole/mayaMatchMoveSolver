/*
 * Copyright (C) 2025 David Cattermole.
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
 * These are bindings to Rust functions - please see Rust code for
 * doc-strings and details.
 */

#ifndef MM_SOLVER_MM_SCENE_GRAPH_STATISTICS_H
#define MM_SOLVER_MM_SCENE_GRAPH_STATISTICS_H

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
Real gaussian(const Real x, const Real mean, const Real sigma) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_mean_absolute_deviation(rust::Slice<const Real> &data, Real &out_mean,
                                  Real &out_mad) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_population_variance(rust::Slice<const Real> &data, Real &out_mean,
                              Real &out_variance) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_sample_variance(rust::Slice<const Real> &data, Real &out_mean,
                          Real &out_variance) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_population_standard_deviation(rust::Slice<const Real> &data,
                                        Real &out_mean,
                                        Real &out_std_dev) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_sample_standard_deviation(rust::Slice<const Real> &data,
                                    Real &out_mean, Real &out_std_dev) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_population_coefficient_of_variation(rust::Slice<const Real> &data,
                                              Real &out_mean,
                                              Real &out_cv) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_sample_coefficient_of_variation(rust::Slice<const Real> &data,
                                          Real &out_mean,
                                          Real &out_cv) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_population_relative_standard_deviation(rust::Slice<const Real> &data,
                                                 Real &out_mean,
                                                 Real &out_rsd) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_sample_relative_standard_deviation(rust::Slice<const Real> &data,
                                             Real &out_mean,
                                             Real &out_rsd) noexcept;

MMSCENEGRAPH_API_EXPORT
Real calc_z_score(const Real mean, const Real std_dev,
                  const Real value) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_peak_to_peak(rust::Slice<const Real> &data, Real &out_value) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_skewness_type1(rust::Slice<const Real> &data, Real &out_mean,
                         Real &out_skewness) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_skewness_type2(rust::Slice<const Real> &data, Real &out_mean,
                         Real &out_skewness) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_population_kurtosis_excess(rust::Slice<const Real> &data,
                                     Real &out_mean,
                                     Real &out_kurtosis) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_sample_kurtosis_excess(rust::Slice<const Real> &data, Real &out_mean,
                                 Real &out_kurtosis) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_local_minima_maxima(rust::Slice<const Real> &data,
                              rust::Vec<size_t> &out_indices) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_signal_to_noise_ratio(rust::Slice<const Real> &data, Real &out_mean,
                                Real &out_snr) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_signal_to_noise_ratio_as_decibels(rust::Slice<const Real> &data,
                                            Real &out_mean,
                                            Real &out_snr_db) noexcept;

// Functions requiring sorted data.
// Note: sorted_data must be sorted in ascending order.

MMSCENEGRAPH_API_EXPORT
bool calc_median_absolute_deviation(rust::Slice<const Real> &sorted_data,
                                    Real &out_median, Real &out_mad) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_median_absolute_deviation_sigma(const Real value,
                                          rust::Slice<const Real> &sorted_data,
                                          Real &out_median,
                                          Real &out_sigma) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_quantile(rust::Slice<const Real> &sorted_data, const Real probability,
                   Real &out_value) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_quartiles(rust::Slice<const Real> &sorted_data, Real &out_q1,
                    Real &out_q2, Real &out_q3) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_interquartile_range(rust::Slice<const Real> &sorted_data,
                              Real &out_median, Real &out_iqr) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_percentile_rank(rust::Slice<const Real> &sorted_data,
                          const Real value, Real &out_rank) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_mean_absolute_error(rust::Slice<const Real> &actual,
                              rust::Slice<const Real> &predicted,
                              Real &out_mae) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_root_mean_square_error(rust::Slice<const Real> &actual,
                                 rust::Slice<const Real> &predicted,
                                 Real &out_rmse) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_normalized_root_mean_square_error(rust::Slice<const Real> &actual,
                                            rust::Slice<const Real> &predicted,
                                            Real &out_nrmse) noexcept;

MMSCENEGRAPH_API_EXPORT
bool calc_coefficient_of_determination(rust::Slice<const Real> &actual,
                                       rust::Slice<const Real> &predicted,
                                       Real &out_r_squared) noexcept;

}  // namespace mmscenegraph

#endif  // MM_SOLVER_MM_SCENE_GRAPH_STATISTICS_H
