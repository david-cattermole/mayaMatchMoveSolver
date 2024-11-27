//
// Copyright (C) 2024 David Cattermole.
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
/// Mathematical statistics functions.
///
/// https://www.calculatorsoup.com/calculators/statistics/descriptivestatistics.php
use anyhow::bail;
use anyhow::Result;
use std::cell::Cell;
use thiserror::Error;

use crate::constant::Real;

#[derive(Error, Debug)]
enum StatisticsError {
    #[error("Data slice cannot be empty.")]
    EmptyDataSlice,

    #[error("Data slice cannot be less than 2.")]
    DataLengthLessThanTwo,

    #[error("Data slice cannot be less than 3.")]
    DataLengthLessThanThree,

    #[error("Data slice cannot be less than 4.")]
    DataLengthLessThanFour,

    #[error("Data slices length does not match.")]
    DataLengthNotEqual,

    #[error("Data must be sorted.")]
    DataNotSorted,

    #[error("Data slice contains non-finite values.")]
    DataContainsNonFiniteValues,

    #[error("Input value cannot be NaN.")]
    InputValueIsNaN,

    #[error("Input value is not finite.")]
    InputValueIsNotFinite,

    #[error("Computed output value is NaN.")]
    OutputValueIsNaN,

    #[error("Computed output value is not finite.")]
    OutputValueIsNotFinite,

    #[error("Computed output value is zero.")]
    OutputValueIsZero,

    #[error("P-value cannot be below 0.0.")]
    PValueIsTooLow,

    #[error("P-value cannot be above 1.0.")]
    PValueIsTooHigh,
}

/// To avoid using using the Rust Compiler 1.82.0, we include this
/// function which provides the same functionality as the is_sorted
/// method.
///
/// https://doc.rust-lang.org/std/primitive.slice.html#method.is_sorted
///
fn is_sorted<T>(data: &[T]) -> bool
where
    T: PartialOrd,
{
    data.windows(2).all(|w| w[0] <= w[1])
}

/// If any value in the given slice is not finite, return false.
fn has_non_finite_values<T>(data: &[Real]) -> bool {
    data.iter().any(|x| !x.is_finite())
}

/// Common trait for statistical computations that don't require
/// sorting.
pub trait UnsortedDataSliceOps {
    /// Returns a reference to the underlying data.
    fn data(&self) -> &[Real];

    /// Computes or returns cached mean.
    fn mean(&self) -> Real;
}

#[derive(Debug)]
pub struct UnsortedDataSlice<'a> {
    data: &'a [Real],

    /// Cached 'mean' value - it's either NaN if it's not computed
    /// yet, or a valid value.
    mean: Cell<Real>,
}

impl<'a> UnsortedDataSlice<'a> {
    /// Creates a new UnsortedDataSlice instance.
    pub fn new(data: &'a [Real], mean: Option<Real>) -> Result<Self> {
        if data.is_empty() {
            bail!(StatisticsError::EmptyDataSlice);
        }

        if cfg!(debug_assertions) {
            if has_non_finite_values::<Real>(data) {
                bail!(StatisticsError::DataContainsNonFiniteValues);
            }
        }

        let mean = match mean {
            Some(value) => {
                assert!(!value.is_nan());
                value
            }
            None => Real::NAN,
        };

        Ok(Self {
            data,
            mean: Cell::new(mean),
        })
    }

    /// Creates a sorted version of the statistics
    pub fn into_sorted(
        self,
        sort_workspace: &'a mut [Real],
    ) -> Result<SortedDataSlice<'a>> {
        if sort_workspace.len() != self.data.len() {
            bail!(StatisticsError::DataLengthNotEqual);
        }

        // Copy data to workspace and sort it
        sort_workspace.copy_from_slice(self.data);
        sort_workspace.sort_by(|a, b| a.partial_cmp(b).unwrap());

        Ok(SortedDataSlice {
            data: sort_workspace,
            mean: self.mean, // Reuse cached values
            median: Cell::new(Real::NAN),
        })
    }
}

impl<'a> UnsortedDataSliceOps for UnsortedDataSlice<'a> {
    fn data(&self) -> &[Real] {
        self.data
    }

    fn mean(&self) -> Real {
        if !self.mean.get().is_nan() {
            self.mean.get()
        } else {
            let mean = calc_mean(self.data)
                .expect("Mean value must be possible for unsorted data slice.");
            self.mean.set(mean);
            mean
        }
    }
}

/// Statistical computations that require sorted data.
pub trait SortedDataSliceOps: UnsortedDataSliceOps {
    /// Computes or returns cached median.
    fn median(&self) -> Real;
}

#[derive(Debug)]
pub struct SortedDataSlice<'a> {
    data: &'a [Real],

    /// Cached 'mean' value - it's either NaN if it's not computed
    /// yet, or a valid value.
    mean: Cell<Real>,

    /// Cached 'median' value - it's either NaN if it's not computed
    /// yet, or a valid value.
    median: Cell<Real>,
}

impl<'a> SortedDataSlice<'a> {
    pub fn new(
        data: &'a [Real],
        mean: Option<Real>,
        median: Option<Real>,
    ) -> Result<Self> {
        if data.is_empty() {
            bail!(StatisticsError::EmptyDataSlice);
        }

        if cfg!(debug_assertions) {
            if has_non_finite_values::<Real>(data) {
                bail!(StatisticsError::DataContainsNonFiniteValues);
            }
        }

        if cfg!(debug_assertions) {
            if !is_sorted(data) {
                bail!(StatisticsError::DataNotSorted);
            }
        }

        let mean = match mean {
            Some(value) => {
                assert!(!value.is_nan());
                value
            }
            None => Real::NAN,
        };

        let median = match median {
            Some(value) => {
                assert!(!value.is_nan());
                value
            }
            None => Real::NAN,
        };

        Ok(Self {
            data,
            mean: Cell::new(mean),
            median: Cell::new(median),
        })
    }

    /// Creates a new SortedDataSlice instance without checking
    /// if the data is sorted.
    pub unsafe fn new_unchecked(
        data: &'a [Real],
        mean: Real,
        median: Real,
    ) -> Self {
        debug_assert!(
            is_sorted(data),
            "Data must be sorted in ascending order"
        );
        debug_assert!(
            has_non_finite_values::<Real>(data),
            "All values must be finite"
        );

        Self {
            data,
            mean: Cell::new(mean),
            median: Cell::new(mean),
        }
    }

    /// Convert to UnsortedStats, which can be used anywhere
    /// UnsortedDataSliceOps is needed.
    pub fn into_unsorted(self) -> UnsortedDataSlice<'a> {
        UnsortedDataSlice {
            data: self.data,
            mean: self.mean,
        }
    }
}

impl<'a> UnsortedDataSliceOps for SortedDataSlice<'a> {
    fn data(&self) -> &[Real] {
        self.data
    }

    fn mean(&self) -> Real {
        if !self.mean.get().is_nan() {
            self.mean.get()
        } else {
            let mean = calc_mean(self.data)
                .expect("Mean value must be possible for sorted data slice.");
            self.mean.set(mean);
            mean
        }
    }
}

impl<'a> SortedDataSliceOps for SortedDataSlice<'a> {
    fn median(&self) -> Real {
        if !self.median.get().is_nan() {
            self.median.get()
        } else {
            let median = calc_median(self.data)
                .expect("Median value must be possible for sorted data slice.");
            debug_assert!(median.is_finite(), "Median must be finite value.");
            self.median.set(median);
            median
        }
    }
}

/// Calculates the value of the Gaussian (normal) probability density function.
///
/// Mathematics:
/// f(x) = exp(-(x-mean)^2/(2*std_dev^2)) where:
/// - exp is the exponential function
/// - mean is the center of the distribution
/// - std_dev is the standard deviation
///
/// Parameters:
/// - x: Input value
/// - mean: Center of the distribution
/// - sigma: Standard deviation
///
/// Returns:
/// - Probability density at x.
/// - Returns unnormalized values (missing 1/sqrt(2) factor for a true
///   PDF).
///
/// Usage:
/// - Model normal distributions
/// - Generate bell curves
/// - Calculate probabilities
/// - Kernel density estimation
pub fn gaussian(x: Real, mean: Real, sigma: Real) -> Real {
    (-((x - mean).powi(2)) / (2.0 * sigma.powi(2))).exp()
}

/// Calculates the arithmetic mean (average) of a dataset.
///
/// Mathematics:
/// mean = sum(x[i])/n where x[i] are individual values and n is the count
///
/// Usage:
/// - Calculate central tendency
/// - Find expected value
/// - Balance point of distribution
///
/// Note:
/// - Sensitive to outliers
/// - Returns None for empty datasets
fn calc_mean(data: &[Real]) -> Result<Real> {
    if data.is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    Ok(data.iter().sum::<Real>() / data.len() as Real)
}

/// Calculates the Mean Absolute Deviation (MAD) of a sorted dataset.
///
/// Mathematics:
/// MAD = average of |value - mean|
///
/// Usage:
/// - Measure average distance from mean
/// - Evaluate data variability
/// - Less sensitive to outliers than variance
/// - Simple measure of dispersion
///
/// Note:
/// - Requires sorted input
/// - Returns units matching input data
/// - More intuitive than variance for some applications
/// - Used in robust statistics
fn calc_mean_absolute_deviation<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    let mean = data_slice.mean();

    // Calculate absolute deviations.
    let deviation_sum: Real =
        data_slice.data().iter().map(|&x| (x - mean).abs()).sum();

    Ok(deviation_sum / data_slice.data().len() as Real)
}

/// Calculates the population variance of a dataset.
///
/// Mathematics:
/// Average of squared differences from the mean
/// variance = sum((value - mean)^2) / count
///
/// Parameters:
/// - data: Slice of values
/// - mean: Pre-calculated population mean
///
/// Returns:
/// - Population variance
///
/// Usage:
/// - Measure spread in complete populations
/// - Calculate variability
/// - Base for other statistical measures
///
/// Note:
/// - Use when data represents entire population
/// - Smaller than sample variance
pub fn calc_population_variance<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    let mean = data_slice.mean();
    if !mean.is_finite() {
        bail!(StatisticsError::InputValueIsNotFinite);
    }

    let variance = data_slice
        .data()
        .iter()
        .map(|&x| (x - mean).powi(2))
        .sum::<Real>()
        / (data_slice.data().len()) as Real; // Bessel's correction

    Ok(variance)
}

/// Calculates the sample variance of a dataset.
///
/// Mathematics:
/// Sum of squared differences from mean divided by (count - 1)
/// variance = sum((value - mean)^2) / (count - 1)
///
/// Parameters:
/// - data: Slice of values
/// - mean: Pre-calculated sample mean
///
/// Returns:
/// - Sample variance
///
/// Usage:
/// - Estimate population variance from sample
/// - Measure spread in samples
/// - Statistical inference
///
/// Note:
/// - Uses (n-1) denominator for unbiased estimate
/// - Larger than population variance
pub fn calc_sample_variance<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().len() < 2 {
        bail!(StatisticsError::DataLengthLessThanTwo);
    }

    let mean = data_slice.mean();
    if !mean.is_finite() {
        bail!(StatisticsError::OutputValueIsNotFinite);
    }

    let sum_squared_diff: Real =
        data_slice.data().iter().map(|&x| (x - mean).powi(2)).sum();
    Ok(sum_squared_diff / (data_slice.data().len() - 1) as Real)
}

/// Calculates the population standard deviation, measuring spread
/// around the mean.
///
/// NOTE: You should calculate the population standard deviation when
/// the dataset you re working with represents an entire population,
/// i.e. every value that you re interested in.
///
/// Mathematics:
/// Square root of population variance
///
/// Parameters:
/// - data: Slice of values
///
/// Returns:
/// - Option<StandardDeviation>: Contains mean and standard deviation
///
/// Usage:
/// - Measure spread in same units as data
/// - Calculate confidence intervals
/// - Quality control
///
/// Note:
/// - Returns None if fewer than 2 values
/// - Use for complete populations only
pub fn calc_population_standard_deviation<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().len() < 2 {
        bail!(StatisticsError::DataLengthLessThanTwo);
    }

    let variance = calc_population_variance(data_slice)?;
    Ok(variance.sqrt())
}

/// Calculates the sample standard deviation, measuring spread around the mean.
///
/// NOTE: You should calculate the sample standard deviation when the
/// dataset you re working with represents a a sample taken from a
/// larger population of interest.
///
/// Mathematics:
/// Square root of sample variance
///
/// Parameters:
/// - data: Slice of values
///
/// Returns:
/// - StandardDeviation: Contains mean and standard deviation
///
/// Usage:
/// - Estimate population standard deviation
/// - Measure sample variability
/// - Statistical inference
///
/// Note:
/// - Uses (n-1) denominator for unbiased estimate
/// - Returns None if fewer than 2 values
pub fn calc_sample_standard_deviation<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().len() < 2 {
        bail!(StatisticsError::DataLengthLessThanTwo);
    }

    let variance = calc_sample_variance(data_slice)?;
    Ok(variance.sqrt())
}

/// Calculates Population Coefficient of Variation (CV).
///
/// The coefficient of variation describes dispersion of data around
/// the mean. It is the ratio of the standard deviation to the mean.
///
/// The coefficient of variation is calculated as the standard
/// deviation divided by the mean.
pub fn calc_population_coefficient_of_variation<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().len() < 2 {
        bail!(StatisticsError::DataLengthLessThanTwo);
    }

    let std_dev = calc_population_standard_deviation(data_slice)?;
    let mean = data_slice.mean();

    Ok(std_dev / mean)
}

/// Calculates Sample Coefficient of Variation (CV).
///
/// The coefficient of variation describes dispersion of data around
/// the mean. It is the ratio of the standard deviation to the mean.
///
/// The coefficient of variation is calculated as the standard
/// deviation divided by the mean.
pub fn calc_sample_coefficient_of_variation<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().len() < 2 {
        bail!(StatisticsError::DataLengthLessThanTwo);
    }

    let mean = data_slice.mean();
    let std_dev = calc_sample_standard_deviation(data_slice)?;

    Ok(std_dev / mean)
}

/// Calculates Population Relative Standard Deviation (RSD)
/// percentage.
///
/// Relative standard deviation describes the variance of a subset of
/// data from the mean.
///
/// It is expressed as a percentage. Relative standard deviation is
/// calculated as the standard deviation times 100 divided by the
/// mean.
pub fn calc_population_relative_standard_deviation<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().len() < 2 {
        bail!(StatisticsError::DataLengthLessThanTwo);
    }

    let std_dev = calc_population_standard_deviation(data_slice)?;
    let mean = data_slice.mean();

    Ok((std_dev * 100.0) / mean)
}

/// Calculates Sample Relative Standard Deviation (RSD) percentage.
///
/// Relative standard deviation describes the variance of a subset of
/// data from the mean.
///
/// It is expressed as a percentage. Relative standard deviation is
/// calculated as the standard deviation times 100 divided by the
/// mean.
pub fn calc_sample_relative_standard_deviation<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().len() < 2 {
        bail!(StatisticsError::DataLengthLessThanTwo);
    }

    let mean = data_slice.mean();
    let std_dev = calc_sample_standard_deviation(data_slice)?;

    Ok((std_dev * 100.0) / mean)
}

/// Calculates how many standard deviations a value is from the mean.
pub fn calc_z_score(mean: Real, std_dev: Real, value: Real) -> Real {
    debug_assert!(mean.is_finite(), "Mean value must be finite value.");
    debug_assert!(
        std_dev.is_finite(),
        "Standard Deviation must be finite value."
    );
    (value - mean) / std_dev.max(1e-10)
}

/// Calculates the range between maximum and minimum values.
///
/// Mathematics:
/// Peak-to-Peak = max(x) - min(x)
///
/// Usage:
/// - Measure total signal amplitude
/// - Identify signal bounds
/// - Quick variability assessment
fn calc_peak_to_peak<T: UnsortedDataSliceOps>(data_slice: &T) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    let max_val = data_slice
        .data()
        .iter()
        .fold(Real::NEG_INFINITY, |a, &b| a.max(b));
    let min_val = data_slice
        .data()
        .iter()
        .fold(Real::INFINITY, |a, &b| a.min(b));

    Ok(max_val - min_val)
}

/// Calculates skewness type 1, measuring asymmetry of distribution.
///
/// The method used in this function is the typical definition used in
/// many older textbooks. Reference:
/// https://www.rdocumentation.org/packages/e1071/versions/1.7-16/topics/skewness
///
/// R code:
///    library(e1071)
///    x = c(2.0, 1.0, 0.0, 1.0, 2.0)
///    # Type 1 is the typical definition used in many older textbooks.
///    skewness(x, type = 1)
///
/// Mathematics:
/// skew = [n/(n-1)(n-2)] * sum((x-mean)/std_dev)^3 where:
/// - n is sample size
/// - mean is average
/// - std_dev is standard deviation
///
/// Usage:
/// - Measure distribution asymmetry
/// - Compare to normal distribution
/// - Identify directional bias
///
/// Note:
/// - Positive values indicate right skew
/// - Negative values indicate left skew
/// - Zero indicates symmetry
fn calc_skewness_type1<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().len() < 2 {
        bail!(StatisticsError::DataLengthLessThanTwo);
    }

    let mean = data_slice.mean();
    let sum_squared_diff: Real = data_slice
        .data()
        .iter()
        .map(|&x| (x - mean).powi(2))
        .sum::<Real>();
    let sum_cubed_diff: Real = data_slice
        .data()
        .iter()
        .map(|&x| (x - mean).powi(3))
        .sum::<Real>();

    if sum_squared_diff == 0.0 {
        bail!(StatisticsError::OutputValueIsZero);
    }

    let n = data_slice.data().len() as Real;
    Ok((sum_cubed_diff / n) / (sum_squared_diff / n).powf(1.5))
}

/// Calculates sample skewness, measuring asymmetry of distribution.
///
/// The method used in this function is used in SAS and SPSS. Reference:
/// https://www.rdocumentation.org/packages/e1071/versions/1.7-16/topics/skewness
///
/// R code:
///    data = c(2.0, 1.0, 0.0, 1.0, 2.0)
///    n <- length(data)
///    mean_data <- mean(data)
///    sd_data <- sd(data)
///    skewness_value <- (n * sum((data - mean_data)^3)) / ((n - 1) * (n - 2) * sd_data^3)
///    skewness_value
///
/// Mathematics:
/// skew = [n/(n-1)(n-2)] * sum((x-mean)/std_dev)^3 where:
/// - n is sample size
/// - mean is average
/// - std_dev is standard deviation
///
/// Usage:
/// - Estimate population skewness
/// - Measure sample asymmetry
/// - Statistical inference
///
/// Note:
/// - Includes bias correction
/// - Standard method in SAS and SPSS
/// - Negative values indicate left skew
fn calc_skewness_type2<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    let mean = data_slice.mean();
    let std_dev = calc_sample_standard_deviation(data_slice)?;

    if std_dev == 0.0 {
        bail!(StatisticsError::OutputValueIsZero);
    }

    let n = data_slice.data().len() as Real;
    let sum_cubed_diff: Real = data_slice
        .data()
        .iter()
        .map(|&x| ((x - mean) / std_dev).powi(3))
        .sum();
    Ok((n / ((n - 1.0) * (n - 2.0))) * sum_cubed_diff)
}

/// Calculates excess kurtosis, measuring "tailedness" of distribution.
///
/// Excess kurtosis describes the height of the tails of a
/// distribution rather than the extremity of the length of the
/// tails. Excess kurtosis means that the distribution has a high
/// frequency of data outliers.
///
/// Mathematics:
/// kurtosis = [1/n * sum((x-mean)/std_dev)^4] - 3 where:
/// - Subtraction of 3 makes normal distribution = 0
///
///
/// Returns:
/// - Excess kurtosis value where:
///   * Positive values indicate heavier tails than normal distribution
///   * Negative values indicate lighter tails than normal distribution
///   * Zero indicates normal-like tail weight
///   * Returns 0.0 for empty datasets or when standard deviation is 0
///
/// Usage:
/// - Measure tail weight relative to normal
/// - Identify outlier presence
/// - Compare to normal distribution
///
/// Note:
/// - Positive values indicate heavy tails
/// - Negative values indicate light tails
/// - Zero indicates normal-like tails
/// - This is the population variant (not sample kurtosis)
/// - Does not account for sample size bias
/// - Sensitive to outliers
fn calc_population_kurtosis_excess<T: UnsortedDataSliceOps>(
    data_slice: &T,
    std_dev: Option<Real>,
) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    let mean = data_slice.mean();
    let std_dev = match std_dev {
        Some(value) => value,
        None => calc_population_standard_deviation(data_slice)?,
    };
    if std_dev == 0.0 {
        bail!(StatisticsError::OutputValueIsZero);
    }

    let n = data_slice.data().len() as Real;
    let fourth_moment = data_slice
        .data()
        .iter()
        .map(|&x| ((x - mean) / std_dev).powi(4))
        .sum::<Real>()
        / n;

    // Calculate excess kurtosis (subtract 3 to make normal
    // distribution = 0).
    let k = fourth_moment - 3.0;

    Ok(k)
}

/// Calculates the sample excess kurtosis of a dataset, which measures
/// how heavy-tailed the distribution is compared to a normal
/// distribution.
///
/// Returns:
/// - Option<Real>: The excess kurtosis value, or None if:
///   - The standard deviation is 0
///   - The dataset has fewer than 4 points
///
/// Usage:
/// - Measure the "tailedness" of a distribution
/// - Detect outliers in a dataset
/// - Compare distributions to normal distribution
///
/// Interpretation:
/// - Positive values indicate heavier tails than normal distribution
/// - Negative values indicate lighter tails than normal distribution
/// - Zero suggests normal distribution-like tails
/// - Larger absolute values indicate more extreme tail behavior
///
/// Note:
/// - This is the sample (unbiased) estimator, suitable for sample data
/// - Requires at least 4 data points
/// - Undefined for zero standard deviation
/// - The correction factor adjusts for sample size bias
fn calc_sample_kurtosis_excess<T: UnsortedDataSliceOps>(
    data_slice: &T,
    std_dev: Option<Real>,
) -> Result<Real> {
    if data_slice.data().len() < 4 {
        bail!(StatisticsError::DataLengthLessThanFour);
    }

    let mean = data_slice.mean();
    let std_dev = match std_dev {
        Some(value) => value,
        None => calc_sample_standard_deviation(data_slice)?,
    };
    if std_dev == 0.0 {
        // Kurtosis is undefined.
        bail!(StatisticsError::OutputValueIsZero);
    }

    // Calculate fourth moment.
    let fourth_moment: Real = data_slice
        .data()
        .iter()
        .map(|&x| ((x - mean) / std_dev).powi(4))
        .sum::<Real>();

    // Calculate kurtosis excess using the formula for samples.
    let n_real = data_slice.data().len() as Real;
    let numerator = n_real * (n_real + 1.0) * fourth_moment;
    let denominator = (n_real - 1.0) * (n_real - 2.0) * (n_real - 3.0);

    let correction_factor =
        (3.0 * (n_real - 1.0).powi(2)) / ((n_real - 2.0) * (n_real - 3.0));

    Ok(numerator / denominator - correction_factor)
}

/// Performs chi-squared test for goodness of fit to normal distribution.
///
/// Mathematics:
/// chi^2 = sum((O - E)^2/E) where:
/// - O is observed frequency
/// - E is expected frequency
///
/// Usage:
/// - Test for normality
/// - Compare observed vs expected frequencies
/// - Evaluate distribution fit
fn calc_population_chi_squared_test<T: UnsortedDataSliceOps>(
    data_slice: &T,
    std_dev: Option<Real>,
) -> Result<Real> {
    let std_dev = match std_dev {
        Some(value) => value,
        None => calc_population_standard_deviation(data_slice)?,
    };
    if std_dev == 0.0 {
        bail!(StatisticsError::OutputValueIsZero);
    }

    // Create histogram bins.
    let n_bins = (data_slice.data().len() as Real).sqrt().round() as usize;
    // TODO: Avoid allocation here.
    let mut hist = vec![0.0; n_bins];

    // Find range for binning.
    let min_val = data_slice
        .data()
        .iter()
        .fold(Real::INFINITY, |a, &b| a.min(b));
    let max_val = data_slice
        .data()
        .iter()
        .fold(Real::NEG_INFINITY, |a, &b| a.max(b));
    let bin_width = (max_val - min_val) / n_bins as Real;

    // Fill histogram.
    for &value in data_slice.data() {
        let bin = ((value - min_val) / bin_width).floor() as usize;
        if bin < n_bins {
            hist[bin] += 1.0;
        }
    }

    // Calculate expected frequencies using normal distribution.
    let mean = data_slice.mean();
    let n = data_slice.data().len() as Real;
    let chi_squared: Real = hist
        .iter()
        .enumerate()
        .map(|(i, &observed)| {
            let bin_center = min_val + (i as Real + 0.5) * bin_width;
            let z = (bin_center - mean) / std_dev;
            let expected = n * bin_width * gaussian(bin_center, mean, std_dev);

            if expected > 0.0 {
                (observed - expected).powi(2) / expected
            } else {
                0.0
            }
        })
        .sum();

    Ok(chi_squared)
}

/// Identifies local extrema (peaks and valleys) in a time series.
///
/// Mathematics:
/// Points where derivative changes sign:
/// - Maximum: x[i-1] < x[i] > x[i+1]
/// - Minimum: x[i-1] > x[i] < x[i+1]
///
/// Usage:
/// - Find peaks and troughs
/// - Identify cycles
/// - Signal analysis
///
/// Note:
/// - Requires at least 3 points.
/// - Returns both maxima and minima.
/// - Simple derivative-based method.
/// - Endpoints (first and last points) cannot be extrema in this
///   implementation.
fn calc_local_minima_maxima<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Vec<usize>> {
    if data_slice.data().len() < 3 {
        bail!(StatisticsError::DataLengthLessThanThree);
    }

    // TODO: Can we guess the capacity of 'points' to avoid reallocation?
    let mut points = Vec::new();

    let data = data_slice.data();
    for i in 1..data.len() - 1 {
        let a = data[i] > data[i - 1] && data[i] > data[i + 1];
        let b = data[i] < data[i - 1] && data[i] < data[i + 1];
        if a || b {
            points.push(i);
        }
    }

    Ok(points)
}

/// Calculates the average power of a discrete-time signal.
///
/// Usage:
/// - Calculate signal strength
/// - Normalize signal amplitudes
/// - Compare signal intensities
/// - Energy analysis
///
/// Note:
/// - Returns 0.0 for empty signals
/// - Always non-negative
/// - Used in signal-to-noise calculations
/// - Represents mean squared amplitude
fn calc_signal_power<T: UnsortedDataSliceOps>(data_slice: &T) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    let n = data_slice.data().len() as Real;
    let sum_squares: Real = data_slice.data().iter().map(|&x| x * x).sum();
    Ok(sum_squares / n)
}

/// Calculates the signal-to-noise ratio of a dataset.
///
/// Mathematics:
/// SNR = P_signal/P_noise where:
/// - P is power (mean squared amplitude)
///
/// Usage:
/// - Measure signal quality
/// - Evaluate measurement precision
/// - Compare signal strengths
///
/// Note:
/// - Returns infinity for perfect signals
/// - Higher values indicate cleaner signals
/// - Often converted to decibels
pub fn calc_signal_to_noise_ratio<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    let mean = data_slice.mean();
    let noise_power = calc_population_variance(data_slice)?;
    let signal_power = calc_signal_power(data_slice)?;

    if noise_power == 0.0 {
        Ok(Real::INFINITY)
    } else {
        Ok(signal_power / noise_power)
    }
}

/// Calculates signal-to-noise ratio (SNR) in decibels.
///
/// Mathematics:
/// SNR = 10 * log10(P_signal/P_noise) where:
/// - P is power (mean squared amplitude)
///
/// Usage:
/// - Measure signal quality
/// - Compare signal strength to noise
/// - Evaluate data quality
pub fn calc_signal_to_noise_ratio_as_decibels<T: UnsortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    let result = calc_signal_to_noise_ratio(data_slice)?;
    if result.is_nan() {
        bail!(StatisticsError::OutputValueIsNaN);
    }

    if result.is_infinite() {
        Ok(result)
    } else {
        // Converts to decibels.
        Ok(10.0 * result.log10())
    }
}

/// Calculates the median (middle value) of sorted data.
///
/// Mathematics:
/// For sorted values:
/// - If odd count: middle value
/// - If even count: average of two middle values
///
/// Parameters:
/// - sorted_data: Slice of Real values, must be sorted
///
/// Returns:
/// - Median value
///
/// Usage:
/// - Find central value
/// - Robust to outliers
/// - Divide data into halves
///
/// Note:
/// - Requires sorted input
/// - More robust than mean for skewed data
fn calc_median(sorted_data: &[Real]) -> Result<Real> {
    if sorted_data.is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }
    if cfg!(debug_assertions) {
        if !is_sorted(sorted_data) {
            bail!(StatisticsError::DataNotSorted);
        }
    }

    let len = sorted_data.len();
    if len % 2 == 0 {
        Ok((sorted_data[len / 2 - 1] + sorted_data[len / 2]) / 2.0)
    } else {
        Ok(sorted_data[len / 2])
    }
}

/// Calculates Median Absolute Deviation (MAD), a robust measure of
/// variability.
///
/// Mathematics:
/// MAD = median(|x[i] - median(X)|) where:
/// - X is the dataset
/// - x[i] are individual values
///
/// Usage:
/// - Robust measure of variability
/// - Outlier detection
/// - Robust alternative to standard deviation
///
/// Note:
/// - Requires sorted input
/// - More robust than standard deviation
/// - Useful for non-normal distributions
pub fn calc_median_absolute_deviation<T: SortedDataSliceOps>(
    data_slice: &T,
    out_sorted_deviations: &mut [Real],
) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }
    if data_slice.data().len() != out_sorted_deviations.len() {
        bail!(StatisticsError::DataLengthNotEqual);
    }

    let median = data_slice.median();

    // Calculate absolute deviations.
    for (i, value) in data_slice.data().iter().enumerate() {
        out_sorted_deviations[i] = (value - median).abs();
    }
    out_sorted_deviations.sort_by(|a, b| a.partial_cmp(b).unwrap());

    Ok(calc_median(&out_sorted_deviations)?)
}

/// Calculates sigma MAD score, measuring how many scaled MAD units a
/// value is from median.
///
/// Mathematics:
/// sigma_mad = (x - median)/(MAD * 1.4826) where:
/// - 1.4826 is scaling factor for normal distribution
///
/// Usage:
/// - Robust outlier detection
/// - Alternative to z-scores
/// - Better for non-normal distributions
pub fn calc_median_absolute_deviation_sigma<T: SortedDataSliceOps>(
    value: Real,
    data_slice: &T,
    out_sorted_deviations: &mut [Real],
) -> Result<Real> {
    if !value.is_finite() {
        bail!(StatisticsError::InputValueIsNotFinite);
    }
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }
    if data_slice.data().len() != out_sorted_deviations.len() {
        bail!(StatisticsError::DataLengthNotEqual);
    }

    let median = calc_median(data_slice.data())?;
    let mad =
        calc_median_absolute_deviation(data_slice, out_sorted_deviations)?;

    // 1.4826 is scaling factor for normal distribution.
    let scaled_mad = mad * 1.4826;

    Ok((value - median) / scaled_mad.max(1e-10))
}

/// Calculate quantile using Type 7 method for interpolation.
///
/// This method uses linear interpolation between modes for continuous
/// samples.  This is the default method in R, Julia, and other
/// statistical packages.
///
/// Arguments:
///   * sorted_data: Slice of Real values, must be sorted in ascending order
///   * probability: Probability (0.0 to 1.0) for the desired quantile
///
/// Returns:
///   * Ok(Real) with the calculated quantile, or Err if input is invalid.
pub fn calc_quantile<T: SortedDataSliceOps>(
    data_slice: &T,
    probability: Real,
) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }
    if probability < 0.0 {
        bail!(StatisticsError::PValueIsTooLow);
    }
    if probability > 1.0 {
        bail!(StatisticsError::PValueIsTooHigh);
    }

    let n = data_slice.data().len();

    // Calculate the theoretical position.
    let h = (n - 1) as Real * probability + 1.0;

    // Get the integer positions for interpolation.
    let i = (h.floor() - 1.0).max(0.0) as usize;
    let j = (h.ceil() - 1.0).min((n - 1) as Real) as usize;

    // Get the actual values at those positions
    let x_i = data_slice.data()[i];
    let x_j = data_slice.data()[j];

    // Calculate interpolation factor.
    let gamma = if i == j { 1.0 } else { h - h.floor() };

    // Perform linear interpolation.
    Ok(x_i + gamma * (x_j - x_i))
}

/// Calculates the quartiles (25th, 50th, and 75th percentiles) of sorted data.
///
/// Usage:
/// - Summarize data distribution.
/// - Create box plots.
/// - Identify outliers.
///
/// Note:
/// - Requires sorted input.
/// - Uses linear interpolation.
/// - Robust to outliers.
pub fn calc_quartiles<T: SortedDataSliceOps>(
    data_slice: &T,
) -> Result<(Real, Real, Real)> {
    let q1 = calc_quantile(data_slice, 0.25)?;
    let q2 = calc_quantile(data_slice, 0.5)?;
    let q3 = calc_quantile(data_slice, 0.75)?;
    Ok((q1, q2, q3))
}

/// Calculates the interquartile range (IQR), the range between 1st
/// and 3rd quartiles.
///
/// Mathematics:
/// IQR = Q3 - Q1 where:
/// - Q1 is the 25th percentile
/// - Q3 is the 75th percentile
///
/// Usage:
/// - Measure statistical dispersion
/// - Identify outliers (1.5xIQR rule)
/// - Create box plots
///
/// Note:
/// - Requires sorted input
/// - Robust to outliers
/// - Used in box plot construction
fn calc_interquartile_range<T: SortedDataSliceOps>(
    data_slice: &T,
) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    let (q1, q2, q3) = calc_quartiles(data_slice)?;

    // Return IQR (Q3 - Q1)
    Ok(q3 - q1)
}

/// Calculate the percentile rank for a single value within a dataset.
///
/// This function determines what percentage of values in the dataset fall below
/// the given value. For example, if a value is at the 75th percentile, 75% of
/// values in the dataset are less than or equal to it.
///
/// Arguments:
///   * data_slice: Slice of data values, must be sorted in ascending order.
///   * value: The value to find the percentile for.
///
/// Returns:
///   * Percentile as a value between 0.0 and 100.0
pub fn calc_percentile_rank<T: SortedDataSliceOps>(
    data_slice: &T,
    value: Real,
) -> Result<Real> {
    if data_slice.data().is_empty() {
        bail!(StatisticsError::EmptyDataSlice);
    }

    let data = data_slice.data();
    let n = data.len();

    // Count values less than our target value
    let mut count = 0;

    for &x in data {
        if x < value {
            count += 1;
        }
    }

    // Calculate percentile rank.
    // Multiply by 100 to get percentage.
    Ok((count as Real / n as Real) * 100.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    const EPSILON: Real = 1e-6;

    fn compute_mean<T: UnsortedDataSliceOps>(data_slice: T) -> Real {
        data_slice.mean()
    }

    #[test]
    fn test_interchangeable_types() {
        let unsorted_data = vec![5.0, 1.0, 3.0, 2.0, 4.0];
        let sorted_data = vec![1.0, 2.0, 3.0, 4.0, 5.0];

        // Create both types of data_slice
        let unsorted = UnsortedDataSlice::new(&unsorted_data, None).unwrap();
        let sorted = SortedDataSlice::new(&sorted_data, None, None).unwrap();

        // Convert sorted to unsorted
        let sorted_as_unsorted = sorted.into_unsorted();

        // Both can be used with the same function
        let mean1 = compute_mean(unsorted);
        let mean2 = compute_mean(sorted_as_unsorted);

        assert_relative_eq!(mean1, mean2, epsilon = EPSILON);
    }

    #[test]
    fn test_unsorted_specific_ops() {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let data_slice = UnsortedDataSlice::new(&data, None).unwrap();
        assert_relative_eq!(data_slice.mean(), 3.0, epsilon = EPSILON);
    }

    #[test]
    fn test_sorted_specific_ops() {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let data_slice = SortedDataSlice::new(&data, None, None).unwrap();
        assert_relative_eq!(data_slice.mean(), 3.0, epsilon = EPSILON);
        assert_relative_eq!(data_slice.median(), 3.0, epsilon = EPSILON);
    }

    #[test]
    fn test_conversion_to_sorted() {
        let data = vec![5.0, 1.0, 3.0, 2.0, 4.0];
        let unsorted = UnsortedDataSlice::new(&data, None).unwrap();

        let mut workspace = vec![0.0; data.len()];
        let sorted = unsorted.into_sorted(&mut workspace).unwrap();

        assert_eq!(sorted.data(), &[1.0, 2.0, 3.0, 4.0, 5.0]);
    }

    #[test]
    fn test_gaussian() {
        let mean = 0.0;
        let std_dev = 1.0;
        // Test standard normal distribution peak at x = mean
        assert_relative_eq!(
            gaussian(mean, mean, std_dev),
            1.0,
            epsilon = EPSILON
        );

        // Test symmetry
        let x1 = 1.0;
        let x2 = -1.0;
        assert_relative_eq!(
            gaussian(x1, mean, std_dev),
            gaussian(x2, mean, std_dev),
            epsilon = EPSILON
        );
    }

    #[test]
    fn test_mean() -> Result<()> {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let result = calc_mean(&data)?;
        assert_relative_eq!(result, 3.0, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_population_standard_deviation() -> Result<()> {
        let data = vec![2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let std_dev = calc_population_standard_deviation(&data_slice)?;
        assert_relative_eq!(data_slice.mean(), 5.0, epsilon = EPSILON);
        assert_relative_eq!(std_dev, 2.0, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_sample_standard_deviation() -> Result<()> {
        let data = vec![2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let std_dev = calc_sample_standard_deviation(&data_slice)?;
        assert_relative_eq!(data_slice.mean(), 5.0, epsilon = EPSILON);
        assert_relative_eq!(std_dev, 2.13808994, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_population_relative_standard_deviation() -> Result<()> {
        let data = vec![2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let rel_std_dev =
            calc_population_relative_standard_deviation(&data_slice)?;
        assert_relative_eq!(data_slice.mean(), 5.0, epsilon = EPSILON);
        assert_relative_eq!(rel_std_dev, 40.0, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_sample_relative_standard_deviation() -> Result<()> {
        let data = vec![2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let rel_std_dev = calc_sample_relative_standard_deviation(&data_slice)?;
        assert_relative_eq!(data_slice.mean(), 5.0, epsilon = EPSILON);
        assert_relative_eq!(rel_std_dev, 42.7617987, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_z_score() -> Result<()> {
        // R code:
        //    data <- c(6.0, 7.0, 7.0, 12.0, 13.0, 13.0, 15.0, 16.0, 19.0, 22.0)
        //    z_scores <- (data-mean(data))/sd(data)
        //    z_scores
        let data =
            vec![6.0, 7.0, 7.0, 12.0, 13.0, 13.0, 15.0, 16.0, 19.0, 22.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let std_dev = calc_sample_standard_deviation(&data_slice)?;
        let expected_z_scores = &[
            -1.3228757, -1.1338934, -1.1338934, -0.1889822, 0.0000000,
            0.0000000, 0.3779645, 0.5669467, 1.1338934, 1.7008401,
        ];
        let mean = data_slice.mean();
        for (value, expected) in data.iter().zip(expected_z_scores) {
            let z_score = calc_z_score(mean, std_dev, *value);
            println!(
                "z_score: value={value} z_score={z_score} expected={expected}"
            );
            assert_relative_eq!(z_score, expected, epsilon = EPSILON);
        }

        Ok(())
    }

    #[test]
    fn test_population_variance() -> Result<()> {
        let data = vec![2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let variance = calc_population_variance(&data_slice)?;
        assert_relative_eq!(variance, 4.0, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_sample_variance() -> Result<()> {
        let data = vec![2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let variance = calc_sample_variance(&data_slice)?;
        assert_relative_eq!(variance, 4.571428571428571, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_peak_to_peak() -> Result<()> {
        let data = vec![1.0, 3.0, -2.0, 4.0, 1.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let value = calc_peak_to_peak(&data_slice)?;
        assert_relative_eq!(value, 6.0, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_skewness_type1() -> Result<()> {
        // Symmetric distribution should have skewness of 0.0.
        //
        // R code:
        //     library(e1071)
        //     x = c(-2.0, -1.0, 0.0, 1.0, 2.0)
        //     skewness(x, type = 1)
        let data = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let skewness = calc_skewness_type1(&data_slice)?;
        assert_relative_eq!(skewness, 0.0, epsilon = EPSILON);

        // Asymmetric distribution should have skewness not equal to 0.0.
        //
        // R code:
        //     library(e1071)
        //     x = c(2.0, 1.0, 0.0, 1.0, 2.0)
        //     skewness(x, type = 1)
        let data = vec![2.0, 1.0, 0.0, 1.0, 2.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let skewness = calc_skewness_type1(&data_slice)?;
        assert_relative_eq!(skewness, -0.3436216, epsilon = EPSILON);

        // Asymmetric distribution should have skewness not equal to 0.0.
        //
        // R code:
        //     library(e1071)
        //     x = c(-2.0, -1.0, 0.0, -1.0, -2.0)
        //     skewness(x, type = 1)
        let data = vec![-2.0, -1.0, 0.0, -1.0, -2.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let skewness = calc_skewness_type1(&data_slice)?;
        assert_relative_eq!(skewness, 0.3436216, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_skewness_type2() -> Result<()> {
        // Symmetric distribution should have skewness of 0.0.
        //
        // R code:
        //     library(e1071)
        //     x = c(-2.0, -1.0, 0.0, 1.0, 2.0)
        //     skewness(x, type = 2)
        let data = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let skewness = calc_skewness_type2(&data_slice)?;
        assert_relative_eq!(skewness, 0.0, epsilon = EPSILON);

        // Asymmetric distribution should have skewness not equal to 0.0.
        //
        // R code:
        //     library(e1071)
        //     x = c(2.0, 1.0, 0.0, 1.0, 2.0)
        //     skewness(x, type = 2)
        let data = vec![2.0, 1.0, 0.0, 1.0, 2.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let skewness = calc_skewness_type2(&data_slice)?;
        assert_relative_eq!(skewness, -0.5122408, epsilon = EPSILON);

        // Asymmetric distribution should have skewness not equal to 0.0.
        //
        // R code:
        //     library(e1071)
        //     x = c(-2.0, -1.0, 0.0, -1.0, -2.0)
        //     skewness(x, type = 2)
        let data = vec![-2.0, -1.0, -0.0, -1.0, -2.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let skewness = calc_skewness_type2(&data_slice)?;
        assert_relative_eq!(skewness, 0.5122408, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_population_kurtosis_excess() -> Result<()> {
        // Normal distribution should have excess kurtosis close to 0
        let data = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let std_dev = calc_population_standard_deviation(&data_slice)?;
        let kurtosis_excess_a =
            calc_population_kurtosis_excess(&data_slice, Some(std_dev))?;
        let kurtosis_excess_b =
            calc_population_kurtosis_excess(&data_slice, None)?;
        assert_relative_eq!(kurtosis_excess_a, -1.3, epsilon = EPSILON);
        assert_relative_eq!(
            kurtosis_excess_a,
            kurtosis_excess_b,
            epsilon = EPSILON
        );

        Ok(())
    }

    #[test]
    fn test_sample_kurtosis_excess() -> Result<()> {
        // Normal distribution should have excess kurtosis close to 0
        let data = vec![-2.0, -1.0, 0.0, 1.0, 2.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let std_dev = calc_sample_standard_deviation(&data_slice)?;
        let kurtosis_excess_a =
            calc_sample_kurtosis_excess(&data_slice, Some(std_dev))?;
        let kurtosis_excess_b = calc_sample_kurtosis_excess(&data_slice, None)?;
        assert_relative_eq!(kurtosis_excess_a, -1.2, epsilon = EPSILON);
        assert_relative_eq!(
            kurtosis_excess_a,
            kurtosis_excess_b,
            epsilon = EPSILON
        );

        Ok(())
    }

    #[test]
    fn test_population_chi_squared() -> Result<()> {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let std_dev = calc_population_standard_deviation(&data_slice)?;
        let chi_squared_a =
            calc_population_chi_squared_test(&data_slice, Some(std_dev))?;
        let chi_squared_b =
            calc_population_chi_squared_test(&data_slice, None)?;
        assert_relative_eq!(chi_squared_a, 8.60323599477829, epsilon = EPSILON);
        assert_relative_eq!(chi_squared_a, chi_squared_b, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_local_minima_maxima() -> Result<()> {
        let data = vec![1.0, 3.0, 2.0, 4.0, 1.0, 5.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let points = calc_local_minima_maxima(&data_slice)?;
        assert_eq!(points, vec![1, 2, 3, 4]);

        Ok(())
    }

    #[test]
    fn test_signal_to_noise_ratio() -> Result<()> {
        // Test clean signal #1
        let data = vec![1.0, 1.0, 1.0, 1.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let snr = calc_signal_to_noise_ratio(&data_slice)?;
        let snr_db = calc_signal_to_noise_ratio_as_decibels(&data_slice)?;
        println!("Clean Signal #1: snr={} snr={}dB", snr, snr_db);
        assert!(snr.is_infinite());

        // Test clean signal #2
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let snr = calc_signal_to_noise_ratio(&data_slice)?;
        let snr_db = calc_signal_to_noise_ratio_as_decibels(&data_slice)?;
        println!("Clean Signal #2: snr={} snr={}dB", snr, snr_db);
        assert!(snr.is_finite());

        // Test noisy signal
        let data = vec![1.0, 1.1, 0.9, 1.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let snr = calc_signal_to_noise_ratio(&data_slice)?;
        let snr_db = calc_signal_to_noise_ratio_as_decibels(&data_slice)?;
        println!("Noisy Signal: snr={} snr={}dB", snr, snr_db);
        assert!(snr.is_finite());

        // Real world #1.
        let data = vec![
            53.0, 65.0, 68.0, 69.0, 70.0, 72.0, 79.0, 84.0, 85.0, 87.0, 89.0,
            90.0, 94.0,
        ];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let snr = calc_signal_to_noise_ratio(&data_slice)?;
        let snr_db = calc_signal_to_noise_ratio_as_decibels(&data_slice)?;
        println!("Real-world Signal: snr={} snr={}dB", snr, snr_db);
        assert!(snr.is_finite());

        Ok(())
    }

    #[test]
    fn test_median() -> Result<()> {
        // Test odd number of elements
        let mut data = vec![1.0, 3.0, 2.0, 5.0, 4.0];
        data.sort_by(|a, b| a.partial_cmp(b).unwrap());
        assert_relative_eq!(calc_median(&data)?, 3.0, epsilon = EPSILON);

        // Test even number of elements
        let mut data = vec![1.0, 2.0, 3.0, 4.0];
        data.sort_by(|a, b| a.partial_cmp(b).unwrap());
        assert_relative_eq!(calc_median(&data)?, 2.5, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_mean_absolute_deviation() -> Result<()> {
        let data = vec![1.0, 1.0, 2.0, 2.0, 4.0, 6.0, 9.0];
        let data_slice = UnsortedDataSlice::new(&data, None)?;
        let value = calc_mean_absolute_deviation(&data_slice)?;
        assert_relative_eq!(value, 2.36734694, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_median_absolute_deviation() -> Result<()> {
        let sorted_data = vec![1.0, 1.0, 2.0, 2.0, 4.0, 6.0, 9.0];
        let mut sorted_deviations: Vec<Real> = vec![0.0; 7];
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        let value = calc_median_absolute_deviation(
            &data_slice,
            &mut sorted_deviations,
        )?;
        assert_relative_eq!(value, 1.0, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_median_absolute_deviation_sigma() -> Result<()> {
        let sorted_data = vec![1.0, 1.0, 2.0, 2.0, 4.0, 6.0, 9.0];
        let mut sorted_deviations: Vec<Real> = vec![0.0; 7];
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        let value = calc_median_absolute_deviation_sigma(
            2.0,
            &data_slice,
            &mut sorted_deviations,
        )?;
        assert_relative_eq!(value, 0.0, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_quantile() -> Result<()> {
        // Test 50% quantile is median value.
        let sorted_data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let median = calc_median(&sorted_data)?;
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        let q2 = calc_quantile(&data_slice, 0.5)?;
        assert_relative_eq!(q2, median, epsilon = EPSILON);

        // Basic quantiles.
        let sorted_data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        let q0 = calc_quantile(&data_slice, 0.0)?;
        let q1 = calc_quantile(&data_slice, 0.25)?;
        let q2 = calc_quantile(&data_slice, 0.5)?;
        let q3 = calc_quantile(&data_slice, 0.75)?;
        let q4 = calc_quantile(&data_slice, 1.0)?;
        assert_relative_eq!(q0, 1.0, epsilon = EPSILON);
        assert_relative_eq!(q1, 2.0, epsilon = EPSILON);
        assert_relative_eq!(q2, 3.0, epsilon = EPSILON);
        assert_relative_eq!(q3, 4.0, epsilon = EPSILON);
        assert_relative_eq!(q4, 5.0, epsilon = EPSILON);

        // Interpolated quantiles.
        let sorted_data = vec![1.0, 2.0, 3.0, 4.0];
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        let q1 = calc_quantile(&data_slice, 0.25)?;
        let q2 = calc_quantile(&data_slice, 0.5)?;
        let q3 = calc_quantile(&data_slice, 0.75)?;
        assert_relative_eq!(q2, 2.5, epsilon = EPSILON);
        assert_relative_eq!(q1, 1.75, epsilon = EPSILON);
        assert_relative_eq!(q3, 3.25, epsilon = EPSILON);

        // Edge cases.
        let single = vec![1.0];
        let data_slice = SortedDataSlice::new(&single, None, None)?;
        let q2 = calc_quantile(&data_slice, 0.5)?;
        assert_relative_eq!(q2, 1.0, epsilon = EPSILON);

        let data = vec![1.0, 2.0];
        let data_slice = SortedDataSlice::new(&data, None, None)?;
        let q2 = calc_quantile(&data_slice, 0.5)?;
        assert_relative_eq!(q2, 1.5, epsilon = EPSILON);

        Ok(())
    }

    #[test]
    fn test_quantiles() -> Result<()> {
        // The below values have been tested against the R programming
        // language values for correctness.
        //
        // R code:
        //     x = c(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0)
        //     quantile(x, probs = c(0,0.25,0.5,0.75,1))
        let sorted_data = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0];
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        let median = calc_median(&sorted_data);
        let (q1, q2, q3) = calc_quartiles(&data_slice)?;
        assert_relative_eq!(q1, 2.5, epsilon = EPSILON); // Q1
        assert_relative_eq!(q2, 4.0, epsilon = EPSILON); // Q2 (median)
        assert_relative_eq!(q3, 5.5, epsilon = EPSILON); // Q3

        Ok(())
    }

    #[test]
    fn test_interquartile_range() -> Result<()> {
        // R code:
        //     x = c(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0)
        //     IQR(x)
        let sorted_data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        assert_relative_eq!(
            calc_interquartile_range(&data_slice).unwrap(),
            2.0,
            epsilon = EPSILON
        );

        // R code:
        //     x = c(53.0, 65.0, 68.0, 69.0, 70.0, 72.0, 79.0, 84.0, 85.0, 87.0, 89.0, 90.0, 94.0)
        //     IQR(x)
        let sorted_data = vec![
            53.0, 65.0, 68.0, 69.0, 70.0, 72.0, 79.0, 84.0, 85.0, 87.0, 89.0,
            90.0, 94.0,
        ];
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        assert_relative_eq!(
            calc_interquartile_range(&data_slice).unwrap(),
            18.0,
            epsilon = EPSILON
        );

        // R code:
        //     x = c(2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0)
        //     IQR(x)
        let sorted_data = vec![2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0];
        let data_slice = SortedDataSlice::new(&sorted_data, None, None)?;
        assert_relative_eq!(
            calc_interquartile_range(&data_slice).unwrap(),
            1.5,
            epsilon = EPSILON
        );

        Ok(())
    }

    #[test]
    fn test_percentile_rank() {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let sorted_slice = SortedDataSlice::new(&data).unwrap();

        assert_eq!(calc_percentile_rank(&sorted_slice, 1.0).unwrap(), 0.0);
        assert_eq!(calc_percentile_rank(&sorted_slice, 3.0).unwrap(), 50.0);
        assert_eq!(calc_percentile_rank(&sorted_slice, 5.0).unwrap(), 100.0);
    }

    #[test]
    fn test_all_percentile_ranks() {
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let sorted_slice = SortedDataSlice::new(&data).unwrap();

        let percentiles = calc_all_percentile_ranks(&sorted_slice).unwrap();
        assert_eq!(percentiles, vec![0.0, 25.0, 50.0, 75.0, 100.0]);
    }
}
