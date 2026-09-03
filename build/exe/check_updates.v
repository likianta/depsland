import compress.szip
import json
import os

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
			println('You are up to date.')
		} else {
        	println('You are up to date (${profile.latest_patch}).')
		}
    } else {
        patch_id := profile.latest_patch

        extract_resources('${proj_dir}/patches/${patch_id}')!
        apply_resources(proj_dir, patch_id, verbose, dry_run)!

        profile.current_patch = profile.latest_patch
        save_record(profile, proj_dir)!
		println('Patch applied (${profile.latest_patch}).')
    }

	os.input('Press Enter or close the console window to exit...')
}

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
