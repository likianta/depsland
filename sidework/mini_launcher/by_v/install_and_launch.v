// check depsland executable, if exists, launch it; else install then run.
// currently this script does not have graphic user interface. we use terminal
// to show the downloading progress.
import json
import net.http
import os

struct Manifest {
	appid   string
	name    string
	version string
	server  string
}

fn main() {
	depsland_path := os.environ()['DEPSLAND']
	if depsland_path == '' {
		// download depsland
		manifest := json.decode(
			Manifest, $embed_file('./manifest.json').to_string()
		)!
		assert manifest.appid != ''

		url := 'http://${manifest.server}/depsland_online_installer.exe'
		// TODO: download to systemp folder
		http.download_file(url, 'depsland_online_installer.exe')!

		os.execvp(
			'depsland_online_installer.exe',
			[manifest.appid, manifest.version, manifest.server]
		)!
	} else {
		if os.exists('${depsland_path}/source/.bin/depsland.exe') {
			// ...
		} else {
			panic('Depsland is broken.')
		}
	}
}

fn download_depsland() {
	// println('Please choose the location to install Depsland program.')
	default_path := '${os.environ()["APPDATA"]}'
	path := os.input(
		'Please choose the location to install Depsland program ' +
		'(${default_path}): '
	)
}
