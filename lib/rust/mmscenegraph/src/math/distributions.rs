/// Calculate mean of a slice of f64.
pub fn mean_of_values(values: &[f64]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    Some(values.iter().sum::<f64>() / values.len() as f64)
}

#[derive(Debug, Copy, Clone)]
pub struct Statistics {
    pub mean: f64,
    pub std_dev: f64,
}

/// Calculate (population) standard deviation of a slice of f64.
pub fn standard_deviation_of_values(values: &[f64]) -> Option<Statistics> {
    if values.len() < 2 {
        // Need at least 2 values for sample std dev
        return None;
    }
    let mean = mean_of_values(values)?;
    let variance = values.iter().map(|&x| (x - mean).powi(2)).sum::<f64>()
        / (values.len()) as f64; // Bessel's correction
    Some(Statistics {
        mean,
        std_dev: variance.sqrt(),
    })
}

/// Gaussian distribution function.
pub fn gaussian(sig: f64, x: f64, mu: f64) -> f64 {
    (-((x - mu).powi(2)) / (2.0 * sig.powi(2))).exp()
}
