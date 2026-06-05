// build mini launcher in v-language.
import compress.szip // https://modules.vlang.io/compress.szip.html#zip_files
import json
import net.http
import os
import regex

struct Manifest {
    appid  string
    name string
    version string
    depsland_ol_url string
}

struct LocalDepslandInfo {
    project_mode string
    depsland_version string
}

fn main() {
    hide_console_window()
    // println('my PID is ${os.getpid()}')

    manifest := json.decode(
        Manifest, $embed_file('_target_meta.json').to_string()
    )!
    println(manifest)

    dps_dir := find_depsland_root()
    dps_approved := if dps_dir == '' { false } else {
        check_version_of_installed_depsland(dps_dir)!
    }
    if dps_dir != '' && !dps_approved {
        println(
            'Detected Depsland installed in your system, but version too ' +
            'low. Will download the latest version from internet now.'
        )
    }
    if dps_approved {
        os.execvp(
            '${dps_dir}/apps/.bin/depsland.exe',
            ['runx', manifest.appid, manifest.version]
        )!
    } else {
        dps_ol_dir := download_and_extract_depsland_ol(
            manifest.depsland_ol_url
        )!
        os.chdir(dps_ol_dir)!
        os.execvp(
            './python/python.exe',
            ['main.py', manifest.appid, manifest.version]
        )!
        cleanup()!
    }
}

fn check_version_of_installed_depsland(path string) !bool {
    info := json.decode(
        LocalDepslandInfo, 
        os.read_file('${path}/.depsland_project.json')!
    )!
    println(info)

    // https://modules.vlang.io/regex.html#RE
    re := regex.regex_opt(r'(\d+)\.(\d+)\.(\d+)(?:([ab])(\d+))?')!
    re.match_string(info.depsland_version)

    major := info.depsland_version[re.groups[0]..re.groups[1]].int()
    minor := info.depsland_version[re.groups[2]..re.groups[3]].int()
    patch := info.depsland_version[re.groups[4]..re.groups[5]].int()
    // https://docs.vlang.io/statements-&-expressions.html#if-expressions
    dev_type := if re.groups[6] == -1 { '' } else {
        info.depsland_version[re.groups[6]..re.groups[7]]
    }
    dev := if re.groups[8] == -1 { -1 } else {
        info.depsland_version[re.groups[8]..re.groups[9]].int()
    }
    
    // the minimal acceptable version is 0.12.0a22
    mut this_version := ''
    mut target_least_version := ''
    if dev == -1 || dev_type == 'b' {
        this_version = '${major:03}.${minor:03}.${patch:03}'
        target_least_version = '000.012.000'
        return this_version >= target_least_version
    } else {
        this_version = '${major:03}.${minor:03}.${patch:03}.${dev:03}'
        target_least_version = '000.012.000.022'
        return this_version >= target_least_version
    }
}

fn cleanup() ! {
    println('Cleanup intermediate files.')
    currdir := os.dir(os.executable())
    os.rm('${currdir}/depsland-online-installer.zip')!
    os.rmdir_all('${currdir}/depsland-online-installer')!
}

fn download_and_extract_depsland_ol(url string) !string {
    // currdir := os.getwd()
    currdir := os.dir(os.executable())
    println('Current executable directory: ${currdir}')
    // url := 'http://172.20.128.100:2188/depsland-online-installer.zip'
    zip := '${currdir}/depsland-online-installer.zip'
    if os.exists(zip) { os.rm(zip)! }
    println('Downloading depsland online installer (~13MB), please wait...')
    // http.download_file(url, zip)!
    // FIXME: the progress doesn't show at time.
    http.download_file_with_progress(url, zip)!
    szip.extract_zip_to_dir(zip, currdir)!
    assert os.exists('${currdir}/depsland-online-installer')
    assert os.exists('${currdir}/depsland-online-installer/main.py')
    assert os.exists('${currdir}/depsland-online-installer/python/python.exe')
    return '${currdir}/depsland-online-installer'
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
