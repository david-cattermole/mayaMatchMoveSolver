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
 */

#include <mmscenegraph/_cxx.h>
#include <mmscenegraph/_cxxbridge.h>
#include <mmscenegraph/statistics.h>

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
Real gaussian(const Real x, const Real mean, const Real sigma) noexcept {
    return shim_gaussian(x, mean, sigma);
}

MMSCENEGRAPH_API_EXPORT
bool calc_mean_absolute_deviation(rust::Slice<const Real> &data, Real &out_mean,
                                  Real &out_mad) noexcept {
    return shim_calc_mean_absolute_deviation(data, out_mean);
}

MMSCENEGRAPH_API_EXPORT
bool calc_population_variance(rust::Slice<const Real> &data, Real &out_mean,
                              Real &out_variance) noexcept {
    return shim_calc_population_variance(data, out_mean, out_variance);
}

MMSCENEGRAPH_API_EXPORT
bool calc_sample_variance(rust::Slice<const Real> &data, Real &out_mean,
                          Real &out_variance) noexcept {
    return shim_calc_sample_variance(data, out_mean, out_variance);
}

MMSCENEGRAPH_API_EXPORT
bool calc_population_standard_deviation(rust::Slice<const Real> &data,
                                        Real &out_mean,
                                        Real &out_std_dev) noexcept {
    return shim_calc_population_standard_deviation(data, out_mean, out_std_dev);
}

MMSCENEGRAPH_API_EXPORT
bool calc_sample_standard_deviation(rust::Slice<const Real> &data,
                                    Real &out_mean,
                                    Real &out_std_dev) noexcept {
    return shim_calc_sample_standard_deviation(data, out_mean, out_std_dev);
}

MMSCENEGRAPH_API_EXPORT
bool calc_population_coefficient_of_variation(rust::Slice<const Real> &data,
                                              Real &out_mean,
                                              Real &out_cv) noexcept {
    return shim_calc_population_coefficient_of_variation(data, out_mean,
                                                         out_cv);
}

MMSCENEGRAPH_API_EXPORT
bool calc_sample_coefficient_of_variation(rust::Slice<const Real> &data,
                                          Real &out_mean,
                                          Real &out_cv) noexcept {
    return shim_calc_sample_coefficient_of_variation(data, out_mean, out_cv);
}

MMSCENEGRAPH_API_EXPORT
bool calc_population_relative_standard_deviation(rust::Slice<const Real> &data,
                                                 Real &out_mean,
                                                 Real &out_rsd) noexcept {
    return shim_calc_population_relative_standard_deviation(data, out_mean,
                                                            out_rsd);
}

MMSCENEGRAPH_API_EXPORT
bool calc_sample_relative_standard_deviation(rust::Slice<const Real> &data,
                                             Real &out_mean,
                                             Real &out_rsd) noexcept {
    return shim_calc_sample_relative_standard_deviation(data, out_mean,
                                                        out_rsd);
}

MMSCENEGRAPH_API_EXPORT
Real calc_z_score(const Real mean, const Real std_dev,
                  const Real value) noexcept {
    return shim_calc_z_score(mean, std_dev, value);
}

MMSCENEGRAPH_API_EXPORT
bool calc_peak_to_peak(rust::Slice<const Real> &data,
                       Real &out_value) noexcept {
    return shim_calc_peak_to_peak(data, out_value);
}

MMSCENEGRAPH_API_EXPORT
bool calc_skewness_type1(rust::Slice<const Real> &data, Real &out_mean,
                         Real &out_skewness) noexcept {
    return shim_calc_skewness_type1(data, out_mean, out_skewness);
}

MMSCENEGRAPH_API_EXPORT
bool calc_skewness_type2(rust::Slice<const Real> &data, Real &out_mean,
                         Real &out_skewness) noexcept {
    return shim_calc_skewness_type2(data, out_mean, out_skewness);
}

MMSCENEGRAPH_API_EXPORT
bool calc_population_kurtosis_excess(rust::Slice<const Real> &data,
                                     Real &out_mean,
                                     Real &out_kurtosis) noexcept {
    return shim_calc_population_kurtosis_excess(data, out_mean, out_kurtosis);
}

MMSCENEGRAPH_API_EXPORT
bool calc_sample_kurtosis_excess(rust::Slice<const Real> &data, Real &out_mean,
                                 Real &out_kurtosis) noexcept {
    return shim_calc_sample_kurtosis_excess(data, out_mean, out_kurtosis);
}

MMSCENEGRAPH_API_EXPORT
bool calc_local_minima_maxima(rust::Slice<const Real> &data,
                              rust::Vec<size_t> &out_indices) noexcept {
    return shim_calc_local_minima_maxima(data, out_indices);
}

MMSCENEGRAPH_API_EXPORT
bool calc_signal_to_noise_ratio(rust::Slice<const Real> &data, Real &out_mean,
                                Real &out_snr) noexcept {
    return shim_calc_signal_to_noise_ratio(data, out_mean, out_snr);
}

MMSCENEGRAPH_API_EXPORT
bool calc_signal_to_noise_ratio_as_decibels(rust::Slice<const Real> &data,
                                            Real &out_mean,
                                            Real &out_snr_db) noexcept {
    return shim_calc_signal_to_noise_ratio_as_decibels(data, out_mean,
                                                       out_snr_db);
}

MMSCENEGRAPH_API_EXPORT
bool calc_median_absolute_deviation(rust::Slice<const Real> &sorted_data,
                                    Real &out_median, Real &out_mad) noexcept {
    return shim_calc_median_absolute_deviation(sorted_data, out_median,
                                               out_mad);
}

MMSCENEGRAPH_API_EXPORT
bool calc_median_absolute_deviation_sigma(const Real value,
                                          rust::Slice<const Real> &sorted_data,
                                          Real &out_median,
                                          Real &out_sigma) noexcept {
    return shim_calc_median_absolute_deviation_sigma(value, sorted_data,
                                                     out_median, out_sigma);
}

MMSCENEGRAPH_API_EXPORT
bool calc_quantile(rust::Slice<const Real> &sorted_data, const Real probability,
                   Real &out_value) noexcept {
    return shim_calc_quantile(sorted_data, probability, out_value);
}

MMSCENEGRAPH_API_EXPORT
bool calc_quartiles(rust::Slice<const Real> &sorted_data, Real &out_q1,
                    Real &out_q2, Real &out_q3) noexcept {
    return shim_calc_quartiles(sorted_data, out_q1, out_q2, out_q3);
}

MMSCENEGRAPH_API_EXPORT
bool calc_interquartile_range(rust::Slice<const Real> &sorted_data,
                              Real &out_median, Real &out_iqr) noexcept {
    return shim_calc_interquartile_range(sorted_data, out_median, out_iqr);
}

MMSCENEGRAPH_API_EXPORT
bool calc_percentile_rank(rust::Slice<const Real> &sorted_data,
                          const Real value, Real &out_rank) noexcept {
    return shim_calc_percentile_rank(sorted_data, value, out_rank);
}

}  // namespace mmscenegraph
