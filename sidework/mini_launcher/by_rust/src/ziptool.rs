// https://github.com/zip-rs/zip2/blob/6c78fe381da074610d99e2d59546b0530bcb6e54/examples/extract.rs
use std::fs;
use std::io;
use zip;

pub fn unzip(file_i: &str, dir_o: &str) -> String {
    let file_handle = fs::File::open(file_i).unwrap();
    let mut archive = zip::ZipArchive::new(file_handle).unwrap();
    for i in 0..archive.len() {
        let mut item = archive.by_index(i).unwrap();
        let relpath = match item.enclosed_name() {
            Some(p) => p,
            None => continue,
        };
        let path_o = format!("{}/{}", dir_o, relpath.display());
        println!("{} -> {}", relpath.display(), path_o);

        if item.is_dir() {
            fs::create_dir_all(path_o).unwrap();
        } else {
            let mut writer = fs::File::create(path_o).unwrap();
            io::copy(&mut item, &mut writer).unwrap();
        }
    }
    dir_o.to_string()
}