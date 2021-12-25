use mmscenegraph_rust;

#[rustfmt::skip]
#[cxx::bridge(namespace = "mmscenegraph")]
pub mod ffi {
    #[namespace = "mmscenegraph"]
    unsafe extern "C++" {
        // C++ includes needed for all files.
        include!("mmscenegraph/_cxx.h");
        include!("mmscenegraph/_symbol_export.h");
    }

    #[derive(Debug, Copy, Clone, Default, PartialEq, PartialOrd)]
    struct Camera {
        sensor_width_mm: f64,
        focal_length_mm: f64,
    }

    #[namespace = "mmscenegraph"]
    extern "Rust" {
        fn foo(number: u32);
        fn foobar(number: u32) -> u32;
        fn make_camera(width: f64, focal: f64) -> Camera;
    }
}

fn foo(number: u32) {
    println!("called Rust with number={}", number);
}

fn foobar(number: u32) -> u32 {
    println!("called Rust with number={}", number);
    number + 1
}

fn make_camera(width: f64, focal: f64) -> ffi::Camera {
    let cam = mmscenegraph_rust::make_camera(width, focal);
    ffi::Camera {
        sensor_width_mm: cam.sensor_width_mm,
        focal_length_mm: cam.focal_length_mm,
    }
}
