// build mini launcher in v-language.
import json
import net.http
import os

struct Manifest {
    appid   string
    name    string
    version string
}

fn main() {
    // println('my PID is ${os.getpid()}')

    root := find_depsland_root()
    if root == '' {
        // new_root := os.input(
        //     'Depsland is not installed, please input a path for the ' +
        //     'installation: '
        // )
        // download_depsland(new_root)!
        panic('Depsland is not installed!')
    }

    manifest := json.decode(
        Manifest, $embed_file('./target.json').to_string()
    )!
    println(manifest)
    os.execvp(
        '${root}/apps/.bin/depsland.exe',
        ['runx', manifest.appid, manifest.version]
    )!
}

fn hide_console_window() {}

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

fn download_depsland(target_directory string)! {
    println(target_directory)
    if !os.exists(target_directory) {
        os.mkdir(target_directory)!
    }
    url := 'http://172.20.128.100:2184/depsland-0.11.0a4.7z'
    http.download_file(url, '${target_directory}/depsland-0.11.0a4.7z')!
}
