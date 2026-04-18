// build mini launcher in v-language.
import compress.szip // https://modules.vlang.io/compress.szip.html#zip_files
import json
import net.http
import os

struct Manifest {
    appid   string
    name    string
    version string
}

fn main() {
    hide_console_window()
    // println('my PID is ${os.getpid()}')

    manifest := json.decode(
        Manifest, $embed_file('./target.json').to_string()
    )!
    println(manifest)

    dps_dir := find_depsland_root()
    if dps_dir == '' {
        dps_ol_dir := download_and_extract_depsland_online_installer()!
        os.chdir(dps_ol_dir)!
        os.execvp(
            './python/python.exe',
            [
                'main.py', 
                manifest.appid, 
                manifest.version
            ]
        )!
        cleanup()!
    } else {
        os.execvp(
            '${dps_dir}/apps/.bin/depsland.exe',
            ['runx', manifest.appid, manifest.version]
        )!
    }
}

fn cleanup() ! {
    println('Cleanup intermediate files.')
    currdir := os.dir(os.executable())
    os.rm('${currdir}/depsland_online_installer.zip')!
    os.rmdir_all('${currdir}/depsland_online_installer')!
}

fn download_and_extract_depsland_online_installer() !string {
    // currdir := os.getwd()
    currdir := os.dir(os.executable())
    println('Current executable directory: ${currdir}')
    url := 'http://172.20.128.100:2188/depsland_online_installer.zip'
    zip := '${currdir}/depsland_online_installer.zip'
    http.download_file(url, zip)!
    szip.extract_zip_to_dir(zip, currdir)!
    assert os.exists('${currdir}/depsland_online_installer')
    assert os.exists('${currdir}/depsland_online_installer/main.py')
    assert os.exists('${currdir}/depsland_online_installer/python/python.exe')
    return '${currdir}/depsland_online_installer'
}

fn find_depsland_root() string {
    // println(os.environ())
    // println(os.environ()['DEPSLAND'])
    depsland_path := os.environ()['DEPSLAND']
    if depsland_path != '' {
        if os.exists('${depsland_path}/apps/.bin/depsland.exe') {
            return depsland_path
        } else {
            panic('Depsland is broken. Path: ${depsland_path}')
        }
    }
    // panic('Depsland not found in your environment.')
    return ''
}

// TODO
fn hide_console_window() {}
