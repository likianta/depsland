import compress.szip
import json
import os
import time

struct Profile {
    appid         string
    latest_patch  string
mut:
    current_patch string
}

fn main() {
	dry_run, verbose := parse_arguments()
    proj_dir := get_project_directory()
	println('Project directory: ${proj_dir}')

    mut profile := json.decode(
		Profile, os.read_file('${proj_dir}/patches/profile.json')!
    )!

    if profile.current_patch == profile.latest_patch {
		if profile.latest_patch == '' {
			println(color('You are up to date.', .green))
		} else {
        	println(
				color('You are up to date (${profile.latest_patch}).', .green)
			)
		}

		if os.exists(
			'${proj_dir}/source/.depsland/mini_deps/depsland_updater'
		) {
			println(color(
				'The updater is going to spwan a subprocess to request ' +
				'available patches from server. You can wait for it done, ' + 
				'or, to prevent this behavior, you can manually close this ' +
				'window at now.',
				.cyan
			))
			if spawn_patch_request(proj_dir) {
				// if patch work exits with code 0, the profile.json may change
				// during the subprocess session. so we need to recheck profile
				// from local disk.
				patch_id, new_patch_available := check_latest_patch(proj_dir)!
				if new_patch_available {
					println(
						'Found new patch (${profile.current_patch} -> ' +
						'${patch_id}), applying...'
					)
					extract_resources('${proj_dir}/patches/${patch_id}')!
					apply_resources(proj_dir, patch_id, verbose, dry_run)!

					profile.current_patch = patch_id
					save_record(profile, proj_dir)!
					println(color('Patch applied (${patch_id}).', .cyan))
				}
			} else {
				println(color('Failed requesting patch from server.', .red))
			}
		}
    } else {
        patch_id := profile.latest_patch

        extract_resources('${proj_dir}/patches/${patch_id}')!
        apply_resources(proj_dir, patch_id, verbose, dry_run)!

        profile.current_patch = patch_id
        save_record(profile, proj_dir)!
		println(color('Patch applied (${patch_id}).', .cyan))
    }

	os.input('Press Enter or close the console window to exit...')
}

// -----------------------------------------------------------------------------

fn apply_resources(
	proj_dir string, patch_id string, verbose bool, dry_run bool
) ! {
	root_i := '${proj_dir}/patches/${patch_id}'
	root_o := '${proj_dir}/source'
    
    assets_map := json.decode(
		map[string]string,
        os.read_file('${root_i}/assets_map.json')!
    )!

	mut relpath := ''
	mut isdir := false // TODO
	mut do_append := false
	mut file_i := ''
	mut file_m := ''
	mut file_o := ''
    
	for file_id, value in assets_map {
		if !dry_run {
			println('Asset: ${value} (${file_id})')
		}

		// e.g. '/path/to/file:11' -> (
		//  relpath='/path/to/file', 
		//  isdir=true, 
		//  do_append=true
		// )
		relpath = value[..value.len - 3]
		isdir = value[value.len - 2..value.len - 1] == '1'
		do_append = value[value.len - 1..] == '1'

		file_i = '${root_i}/assets/${file_id}'
		file_m = '${root_i}/backups/${file_id}'
		file_o = '${root_o}/${relpath}'
		
		if dry_run {
			node_type := if isdir { 'dir' } else { 'file' }
			if do_append {
				if os.exists(file_o) {
					println(
						'[dry_run] Update ${node_type} '
						+ '"source/${relpath}" (${file_id})'
					)
				} else {
					println(
						'[dry_run] Append ${node_type} '
						+ '"source/${relpath}" (${file_id})'
					)
				}
			} else {
				println(
					'[dry_run] Delete ${node_type} '
					+ '"source/${relpath}" (${file_id})'
				)
			}
		} else {
			if verbose {
				println(
					'[verbose] \n' +
					'    value=${value}; \n' +
				    '    file_i=${file_i}; \n' +
					'    file_o=${file_o}; \n' +
					'    do_append=${do_append}; \n' +
					'    target_exists=${os.exists(file_o)}'
				)
			}
			if do_append {
				if os.exists(file_o) {
					os.mv(file_o, file_m)!
				}
				os.mv(file_i, file_o)!
			} else {
				if os.exists(file_o) {
					os.mv(file_o, file_m)!
				}
			}
		}
	}
}

fn check_latest_patch(proj_dir string) !(string, bool) {
	profile := json.decode(
		Profile, os.read_file('${proj_dir}/patches/profile.json')!
    )!
	return profile.latest_patch, profile.current_patch == profile.latest_patch
}

enum Color {
	black = 30
	red = 31
	green = 32
	yellow = 33
	blue = 34
	magenta = 35
	cyan = 36
	white = 37
}

fn color(text string, color_ Color) string {
	// usage: println(color('hello', .green))
	return '\x1b[${int(color_)}m${text}\x1b[0m'
}

fn extract_resources(patch_dir string) ! {
	println('Patch directory: ${patch_dir}')

	if !os.exists('${patch_dir}/assets') {
        // we have downloaded the patch in some way, but not extracted yet.
        println('Extract resources from "assets.zip".')
        assert os.exists('${patch_dir}/assets.zip')
        szip.extract_zip_to_dir('${patch_dir}/assets.zip', patch_dir)!
        if !os.exists('${patch_dir}/backups') {
            os.mkdir('${patch_dir}/backups')!
        }
	}

	assert os.exists('${patch_dir}/assets')
	assert os.exists('${patch_dir}/assets_map.json')
	assert os.exists('${patch_dir}/backups')
	assert os.exists('${patch_dir}/manifest.pkl')
}

fn get_project_directory() string {
    curr_dir := os.dir(os.executable())
	println('Current executable directory: ${curr_dir}')

    assert os.exists('${curr_dir}/patches')
    assert os.exists('${curr_dir}/patches/history.txt')
    assert os.exists('${curr_dir}/patches/profile.json')
    // assert os.exists('${curr_dir}/python')
    assert os.exists('${curr_dir}/source')
	
	return curr_dir.replace('\\', '/')
}

fn parse_arguments() (bool, bool) {
	args := arguments()[1..]
	dry_run := '-d' in args || '--debug' in args || '--dry-run' in args
	verbose := '-v' in args || '--verbose' in args
	return dry_run, verbose
}

fn save_record(profile Profile, proj_dir string) ! {
	history_file := '${proj_dir}/patches/history.txt'
    // assert os.exists(history_file)
    old_history := os.read_file(history_file)!
    new_history := '${profile.latest_patch}\n${old_history}'
    os.write_file(history_file, new_history)!

    json_str := json.encode(profile)
    os.write_file('${proj_dir}/patches/profile.json', json_str)!
}

fn spawn_patch_request(proj_dir string) bool {
	// https://chatgpt.com/share/6aa11917-d214-83ee-b737-1895be702072

	mut proc := os.new_process('${proj_dir}/python/python.exe')

	// proc.set_work_folder('${proj_dir}/source/.depsland/mini_deps')
	// proc.set_work_folder(proj_dir)
	proc.set_work_folder('${proj_dir}/source')
	//	set working dir to $proj_dir or $proj_dir/source. this is required by 
	//	`depsland/gui/patch_maker_online/air_client.py:_init_remote_env
	//	:proj_dir`.

	// set environ
	// (a)
	// os.setenv('PYTHONPATH', 'source;source/.depsland/mini_deps')
	// os.setenv('PYTHONUTF8', '1')
	// os.setenv('NEOPRINT_LEGACY_WINDOWS', '1')
	// (b)
	// proc.set_environment({
	// 	'PYTHONPATH': '.',
	// 	'PYTHONUTF8': '1',
	// 	'NEOPRINT_LEGACY_WINDOWS': '1'
	// })
	// (c)
	mut env := os.environ()
	env['PYTHONPATH'] = '.;.depsland/mini_deps'
	// env['PYTHONPATH'] = (
	// 	'${proj_dir}/source;${proj_dir}/source/.depsland/mini_deps'
	// )
	env['PYTHONUTF8'] = '1'
	env['NEOPRINT_LEGACY_WINDOWS'] = '1'
	proc.set_environment(env)

	if os.exists(
		'${proj_dir}/source/.depsland/mini_deps/depsland_updater/__main__.py'
	) {
		// the canonical way
		proc.set_args(['-u', '-m', 'depsland_updater', 'patch_online'])	
	} else {
		// in some old versions, tree-shaking may not include "__main__.py" to 
		// `.../mini_deps/depsland_updater`, so we fallback to the script 
		// entrance.
		proc.set_args([
			'-u', 
			'${proj_dir}/source/.depsland/mini_deps/depsland_updater' +
			'/patch_client.py'
		])
	}

	// redirect stdio to main console.
	proc.set_redirect_stdio()

	// start asynchronously
	proc.run()
	println('Python process started (PID ${proc.pid})')
	
	exit_code := drain_output(mut proc)
	proc.wait()
	proc.close()
	return exit_code == 0
}

fn drain_output(mut process os.Process) int {
	for process.is_alive() {
		if output := process.pipe_read(.stdout) {
			print(output)
		} else if output := process.pipe_read(.stderr) {
			print(color(output, .red))
		} else {
			time.sleep(50 * time.millisecond)
		}
	}
	if output := process.pipe_read(.stdout) {
		print(output)
	} else if output := process.pipe_read(.stderr) {
		print(color(output, .red))
	}
	if process.code != 0 {
		'Error occurred in Python process (exit code ${process.code})'
	}
	return process.code
}
