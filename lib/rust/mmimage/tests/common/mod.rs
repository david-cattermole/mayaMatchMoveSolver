use anyhow::bail;
use anyhow::Result;
use log::debug;
use log::warn;
use std::path::Path;
use std::path::PathBuf;

pub fn construct_image_file_paths(
    base_dir: &Path,
    file_names: &[&str],
) -> Result<Vec<PathBuf>> {
    let mut file_paths = Vec::with_capacity(file_names.len());
    for file_name in file_names {
        let mut file_path = PathBuf::new();
        file_path.push(base_dir);
        file_path.push(file_name);
        if file_path.is_file() {
            file_paths.push(file_path);
        } else {
            warn!("Could not find file name {:?}", file_path);
        }
    }
    if file_paths.len() == 0 {
        bail!("Could not find any valid image file paths.")
    } else {
        Ok(file_paths)
    }
}

pub fn find_openexr_images_dir() -> Result<PathBuf> {
    // '/home/user/dev/mayaMatchMoveSolver/lib/rust/mmimage'
    let cargo_manifest_path: &'static str = env!("CARGO_MANIFEST_DIR");
    debug!("cargo_manifest_path={cargo_manifest_path:?}");

    let abs_file_path = std::path::absolute(Path::new(&cargo_manifest_path))?;
    let mut pathbuf = PathBuf::from(abs_file_path);
    debug!("pathbuf={pathbuf:?}");

    // Strips down to project directory:
    // '/home/user/dev/mayaMatchMoveSolver/'
    let mut i = 0;
    while i < 3 {
        pathbuf.pop();
        i += 1;
    }
    debug!("pathbuf={pathbuf:?}");

    // '/home/user/dev/mayaMatchMoveSolver/tests/data/openexr-images/'
    pathbuf.push("tests");
    pathbuf.push("data");
    pathbuf.push("openexr-images");
    debug!("pathbuf={pathbuf:?}");

    if pathbuf.is_dir() {
        Ok(pathbuf)
    } else {
        bail!("Could not find openexr-images directory.")
    }
}
