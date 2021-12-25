pub struct Camera {
    pub sensor_width_mm: f64,
    pub focal_length_mm: f64,
}

pub fn make_camera(width: f64, focal: f64) -> Camera {
    println!("Make camera. width={} focal={}", width, focal);
    Camera {
        sensor_width_mm: width,
        focal_length_mm: focal,
    }
}

pub fn make_camera_default() -> Camera {
    println!("Make default camera.");
    let width = 36.0;
    let focal = 50.0;
    make_camera(width, focal)
}
