mod downloader;
mod ziptool;

// use downloader::download;
use serde_json::Value;
// use std::env;
use std::fs;
use std::io::{Write, stdin, stdout};
use std::path::Path;
use std::process::Command;

fn main() {
    // let key = "PATH";
    // let val = env::var(key).unwrap();
    // println!("{}: {:?}", key, val);

    let json_str = include_str!("res/target_app_info.json");
    let json: Value = serde_json::from_str(json_str).unwrap();
    println!("{}", json);

    // TEST: what if DEPSLAND not exists in os environment...
    let debug_mode = true;
    // let mut depsland_zip = String::new();
    let depsland_zip: String;
    if debug_mode {
        let x = input(concat!(
            "The depsland launcher is missing. ",
            "Would you like to download it now? [Y/n]",
        ))
        .to_lowercase();
        if x == "y" || x == "" {
            let path = input(
                "Please enter the installation folder:"
            );
            // assert inexist or empty
            if fs::exists(&path).is_ok() {
                if fs::read_dir(&path).is_ok() {
                    println!("Folder already exists.");
                    return;
                }
            } else {
                fs::create_dir(&path).unwrap();
            }
            depsland_zip = download_depsland(&path);
        } else {
            println!("User cancelled.");
            return;
        }
    } else {
        // ...
        return;
    }
    
    assert!(depsland_zip.len() > 0);
    let root = ziptool::unzip(
        &depsland_zip,
        Path::new(&depsland_zip).parent().unwrap().to_str().unwrap()
    );
    
    Command::new(format!("{}/python/python.exe", root)).arg("-V");

    // check if "DEPSLAND" in the env.
    // match env::var("DEPSLAND") {
    //     Ok(val) => {
    //         println!("Depsland exists at {}", val);
    //         // bring up depsland process
    //         // https://stackoverflow.com/a/25574952/9695911
    //         Command::new(format!("{val}/apps/.bin/depsland.exe"))
    //             .arg("runx")
    //             .arg(json.get("appid").unwrap().to_string())
    //             .arg(json.get("version").unwrap().to_string())
    //             .status()
    //             .expect("0");
    //     }
    //     Err(_) => {
    //         // download depsland
    //         // warning: this is time consuming!
    //         println!("TODO: Download depsland from the net.");
    //         // ...
    //     }
    // }
}

fn input(prompt: &str) -> String {
    print!("{} ", prompt);
    let _ = stdout().flush();
    let mut user_data = String::new();
    stdin().read_line(&mut user_data).expect("Invalid input");
    if let Some('\n') = user_data.chars().last() {
        user_data.pop();
    }
    if let Some('\r') = user_data.chars().last() {
        user_data.pop();
    }
    user_data
}

fn download_depsland(folder: &str) -> String {
    // TODO: show progress in UI.
    let file_o = format!("{folder}/depsland-0.9.0b5-windows.7z");
    downloader::download(
        "http://172.20.128.100:2135/depsland-dist/depsland-0.9.0b5-windows.7z",
        &file_o,
    )
    .unwrap();
    file_o
}
