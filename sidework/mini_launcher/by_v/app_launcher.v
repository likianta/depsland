// build mini launcher in v-language.
import os

fn main() {
    root := find_depsland_root()
    appid := 'asa_gui'
    version := '0.15.0a15'
    run_app(root, appid, version)
}

fn find_depsland_root() string {
    depsland_path := os.environ()['DEPSLAND']
    if depsland_path {
        if os.exists('${depsland_path}/source/.bin/depsland.exe') {
            return depsland_path
        }
    }
    panic('Depsland not found in your environment.')
}
