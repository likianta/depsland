use std::fs::File;
use std::io::Write;
use std::error::Error;
use reqwest;

pub fn download(url: &str, dst: &str) -> Result<(), Box<dyn Error>> {
    let rsp = reqwest::blocking::get(url)?;
    let mut file = File::create(dst)?;
    let data = rsp.bytes()?;
    file.write_all(&data)?;
    // drop(file);  // close
    Ok(())
}
