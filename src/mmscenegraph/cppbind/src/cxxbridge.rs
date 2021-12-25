#[rustfmt::skip]
#[cxx::bridge(namespace = "mmscenegraph")]
pub mod ffi {
    #[namespace = "mmscenegraph"]
    unsafe extern "C++" {
        // C++ includes needed for all files.
        include!("mmscenegraph/_cxx.h");
        include!("mmscenegraph/_symbol_export.h");
    }

    #[namespace = "mmscenegraph"]
    extern "Rust" {
        fn foo(number: u32);

        fn foobar(number: u32) -> u32;
    }
}

fn foo(number: u32) {
    println!("called Rust with number={}", number);
}

fn foobar(number: u32) -> u32 {
    println!("called Rust with number={}", number);
    number + 1
}
