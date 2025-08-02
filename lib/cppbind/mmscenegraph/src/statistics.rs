//
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
//

use mmscenegraph_rust::constant::Real as CoreReal;
use mmscenegraph_rust::math::statistics::{
    calc_coefficient_of_determination as core_calc_coefficient_of_determination,
    calc_interquartile_range as core_calc_interquartile_range,
    calc_local_minima_maxima as core_calc_local_minima_maxima,
    calc_mean_absolute_deviation as core_calc_mean_absolute_deviation,
    calc_mean_absolute_error as core_calc_mean_absolute_error,
    calc_median_absolute_deviation as core_calc_median_absolute_deviation,
    calc_median_absolute_deviation_sigma as core_calc_median_absolute_deviation_sigma,
    calc_normalized_root_mean_square_error as core_calc_normalized_root_mean_square_error,
    calc_peak_to_peak as core_calc_peak_to_peak,
    calc_percentile_rank as core_calc_percentile_rank,
    calc_population_coefficient_of_variation as core_calc_population_coefficient_of_variation,
    calc_population_kurtosis_excess as core_calc_population_kurtosis_excess,
    calc_population_relative_standard_deviation as core_calc_population_relative_standard_deviation,
    calc_population_standard_deviation as core_calc_population_standard_deviation,
    calc_population_variance as core_calc_population_variance,
    calc_quantile as core_calc_quantile, calc_quartiles as core_calc_quartiles,
    calc_root_mean_square_error as core_calc_root_mean_square_error,
    calc_sample_coefficient_of_variation as core_calc_sample_coefficient_of_variation,
    calc_sample_kurtosis_excess as core_calc_sample_kurtosis_excess,
    calc_sample_relative_standard_deviation as core_calc_sample_relative_standard_deviation,
    calc_sample_standard_deviation as core_calc_sample_standard_deviation,
    calc_sample_variance as core_calc_sample_variance,
    calc_signal_to_noise_ratio as core_calc_signal_to_noise_ratio,
    calc_signal_to_noise_ratio_as_decibels as core_calc_signal_to_noise_ratio_as_decibels,
    calc_skewness_type1 as core_calc_skewness_type1,
    calc_skewness_type2 as core_calc_skewness_type2,
    calc_z_score as core_calc_z_score, gaussian as core_gaussian,
    SortedDataSlice, SortedDataSliceOps, UnsortedDataSlice,
    UnsortedDataSliceOps,
};

pub fn shim_gaussian(x: CoreReal, mean: CoreReal, sigma: CoreReal) -> CoreReal {
    core_gaussian(x, mean, sigma)
}

pub fn shim_calc_mean_absolute_deviation(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_mean_absolute_deviation(&data_slice) {
                Ok(_mad) => {
                    *out_mean = data_slice.mean();
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_population_variance(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_variance: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => match core_calc_population_variance(&data_slice) {
            Ok(variance) => {
                *out_mean = data_slice.mean();
                *out_variance = variance;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_sample_variance(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_variance: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => match core_calc_sample_variance(&data_slice) {
            Ok(variance) => {
                *out_mean = data_slice.mean();
                *out_variance = variance;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_population_standard_deviation(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_std_dev: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_population_standard_deviation(&data_slice) {
                Ok(std_dev) => {
                    *out_mean = data_slice.mean();
                    *out_std_dev = std_dev;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_sample_standard_deviation(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_std_dev: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_sample_standard_deviation(&data_slice) {
                Ok(std_dev) => {
                    *out_mean = data_slice.mean();
                    *out_std_dev = std_dev;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_population_coefficient_of_variation(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_cv: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_population_coefficient_of_variation(&data_slice) {
                Ok(cv) => {
                    *out_mean = data_slice.mean();
                    *out_cv = cv;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_sample_coefficient_of_variation(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_cv: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_sample_coefficient_of_variation(&data_slice) {
                Ok(cv) => {
                    *out_mean = data_slice.mean();
                    *out_cv = cv;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_population_relative_standard_deviation(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_rsd: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_population_relative_standard_deviation(&data_slice)
            {
                Ok(rsd) => {
                    *out_mean = data_slice.mean();
                    *out_rsd = rsd;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_sample_relative_standard_deviation(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_rsd: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_sample_relative_standard_deviation(&data_slice) {
                Ok(rsd) => {
                    *out_mean = data_slice.mean();
                    *out_rsd = rsd;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_z_score(
    mean: CoreReal,
    std_dev: CoreReal,
    value: CoreReal,
) -> CoreReal {
    core_calc_z_score(mean, std_dev, value)
}

pub fn shim_calc_peak_to_peak(
    data: &[CoreReal],
    out_value: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => match core_calc_peak_to_peak(&data_slice) {
            Ok(value) => {
                *out_value = value;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_skewness_type1(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_skewness: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => match core_calc_skewness_type1(&data_slice) {
            Ok(skewness) => {
                *out_mean = data_slice.mean();
                *out_skewness = skewness;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_skewness_type2(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_skewness: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => match core_calc_skewness_type2(&data_slice) {
            Ok(skewness) => {
                *out_mean = data_slice.mean();
                *out_skewness = skewness;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_population_kurtosis_excess(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_kurtosis: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_population_kurtosis_excess(&data_slice, None) {
                Ok(kurtosis) => {
                    *out_mean = data_slice.mean();
                    *out_kurtosis = kurtosis;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_sample_kurtosis_excess(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_kurtosis: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_sample_kurtosis_excess(&data_slice, None) {
                Ok(kurtosis) => {
                    *out_mean = data_slice.mean();
                    *out_kurtosis = kurtosis;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_local_minima_maxima(
    data: &[CoreReal],
    out_indices: &mut Vec<usize>,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => match core_calc_local_minima_maxima(&data_slice) {
            Ok(indices) => {
                *out_indices = indices;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_signal_to_noise_ratio(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_snr: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => match core_calc_signal_to_noise_ratio(&data_slice) {
            Ok(snr) => {
                *out_mean = data_slice.mean();
                *out_snr = snr;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_signal_to_noise_ratio_as_decibels(
    data: &[CoreReal],
    out_mean: &mut CoreReal,
    out_snr_db: &mut CoreReal,
) -> bool {
    match UnsortedDataSlice::new(data, None) {
        Ok(data_slice) => {
            match core_calc_signal_to_noise_ratio_as_decibels(&data_slice) {
                Ok(snr_db) => {
                    *out_mean = data_slice.mean();
                    *out_snr_db = snr_db;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_median_absolute_deviation(
    sorted_data: &[CoreReal],
    out_median: &mut CoreReal,
    out_mad: &mut CoreReal,
) -> bool {
    match SortedDataSlice::new(sorted_data, None, None) {
        Ok(data_slice) => {
            let mut sorted_deviations = vec![0.0; sorted_data.len()];
            match core_calc_median_absolute_deviation(
                &data_slice,
                &mut sorted_deviations,
            ) {
                Ok(mad) => {
                    *out_median = data_slice.median();
                    *out_mad = mad;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_median_absolute_deviation_sigma(
    value: CoreReal,
    sorted_data: &[CoreReal],
    out_median: &mut CoreReal,
    out_sigma: &mut CoreReal,
) -> bool {
    match SortedDataSlice::new(sorted_data, None, None) {
        Ok(data_slice) => {
            let mut sorted_deviations = vec![0.0; sorted_data.len()];
            match core_calc_median_absolute_deviation_sigma(
                value,
                &data_slice,
                &mut sorted_deviations,
            ) {
                Ok(sigma) => {
                    *out_median = data_slice.median();
                    *out_sigma = sigma;
                    true
                }
                Err(_) => false,
            }
        }
        Err(_) => false,
    }
}

pub fn shim_calc_quantile(
    sorted_data: &[CoreReal],
    probability: CoreReal,
    out_value: &mut CoreReal,
) -> bool {
    match SortedDataSlice::new(sorted_data, None, None) {
        Ok(data_slice) => match core_calc_quantile(&data_slice, probability) {
            Ok(value) => {
                *out_value = value;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_quartiles(
    sorted_data: &[CoreReal],
    out_q1: &mut CoreReal,
    out_q2: &mut CoreReal,
    out_q3: &mut CoreReal,
) -> bool {
    match SortedDataSlice::new(sorted_data, None, None) {
        Ok(data_slice) => match core_calc_quartiles(&data_slice) {
            Ok((q1, q2, q3)) => {
                *out_q1 = q1;
                *out_q2 = q2;
                *out_q3 = q3;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_interquartile_range(
    sorted_data: &[CoreReal],
    out_median: &mut CoreReal,
    out_iqr: &mut CoreReal,
) -> bool {
    match SortedDataSlice::new(sorted_data, None, None) {
        Ok(data_slice) => match core_calc_interquartile_range(&data_slice) {
            Ok(iqr) => {
                *out_median = data_slice.median();
                *out_iqr = iqr;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_percentile_rank(
    sorted_data: &[CoreReal],
    value: CoreReal,
    out_rank: &mut CoreReal,
) -> bool {
    match SortedDataSlice::new(sorted_data, None, None) {
        Ok(data_slice) => match core_calc_percentile_rank(&data_slice, value) {
            Ok(rank) => {
                *out_rank = rank;
                true
            }
            Err(_) => false,
        },
        Err(_) => false,
    }
}

pub fn shim_calc_mean_absolute_error(
    actual: &[CoreReal],
    predicted: &[CoreReal],
    out_mae: &mut CoreReal,
) -> bool {
    match core_calc_mean_absolute_error(actual, predicted) {
        Ok(mae) => {
            *out_mae = mae;
            true
        }
        Err(_) => false,
    }
}

pub fn shim_calc_root_mean_square_error(
    actual: &[CoreReal],
    predicted: &[CoreReal],
    out_rmse: &mut CoreReal,
) -> bool {
    match core_calc_root_mean_square_error(actual, predicted) {
        Ok(rmse) => {
            *out_rmse = rmse;
            true
        }
        Err(_) => false,
    }
}

pub fn shim_calc_normalized_root_mean_square_error(
    actual: &[CoreReal],
    predicted: &[CoreReal],
    out_nrmse: &mut CoreReal,
) -> bool {
    match core_calc_normalized_root_mean_square_error(actual, predicted) {
        Ok(nrmse) => {
            *out_nrmse = nrmse;
            true
        }
        Err(_) => false,
    }
}

pub fn shim_calc_coefficient_of_determination(
    actual: &[CoreReal],
    predicted: &[CoreReal],
    out_r_squared: &mut CoreReal,
) -> bool {
    match core_calc_coefficient_of_determination(actual, predicted) {
        Ok(r_squared) => {
            *out_r_squared = r_squared;
            true
        }
        Err(_) => false,
    }
}
