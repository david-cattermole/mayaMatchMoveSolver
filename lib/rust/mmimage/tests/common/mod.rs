use anyhow::bail;
use anyhow::Result;
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
    let directory = PathBuf::from("C:/Users/catte/dev/openexr-images/");
    if directory.is_dir() {
        Ok(directory)
    } else {
        bail!("Could not find openexr-images directory.")
    }
}
