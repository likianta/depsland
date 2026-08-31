import compress.szip
import json
import os

fn main() {
	dry_run, verbose := parse_arguments()

	patch_id := get_patch_id()
	println('Patch ID: ${patch_id}')

	projdir := locate_target_directory()!
	root_i := '${projdir}/patches/${patch_id}'
	root_o := '${projdir}/source'
	
	assets_map := extract_resources(projdir, patch_id)!

	// apply patch
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
	
	save_record(patch_id, '${projdir}/patches')!
	os.input('Patch applied. Press Enter to exit... ')
}

fn extract_resources(projdir string, patch_id string) !map[string]string {
	// init directories
	patch_dir := '${projdir}/patches/${patch_id}'
	if os.exists(patch_dir) {
		assert os.exists('${patch_dir}/assets')
		assert os.exists('${patch_dir}/assets_map.json')
		assert os.exists('${patch_dir}/backups')
		assert os.exists('${patch_dir}/manifest.pkl')
		// remove above except 'backups'
		os.rmdir_all('${patch_dir}/assets')!
		os.rm('${patch_dir}/assets_map.json')!
		os.rm('${patch_dir}/manifest.pkl')!
	} else {
		os.mkdir(patch_dir)!
		os.mkdir('${patch_dir}/backups')!
	}
	
	assets_map_data := $embed_file('./grocery/assets_map.json')
	assets_zip_data := $embed_file('./grocery/assets.zip')
	manifest_data := $embed_file('./grocery/manifest.pkl')
	os.write_bytes('${patch_dir}/assets_map.json', assets_map_data.to_bytes())!
	os.write_bytes('${patch_dir}/assets.zip', assets_zip_data.to_bytes())!
	os.write_bytes('${patch_dir}/manifest.pkl', manifest_data.to_bytes())!
	szip.extract_zip_to_dir('${patch_dir}/assets.zip', patch_dir)!
	assert os.exists('${patch_dir}/assets')

	return json.decode(
		map[string]string, assets_map_data.to_string()
	)!
}

fn get_patch_id() string {
	// try to get patch id from command line arguments. if not exists, turn to
	// extract it from self file name.
	args := arguments()[1..]
	mut patch_id := ''
	if '--patch-id' in args {
		idx := args.index('--patch-id')
		patch_id = args[idx + 1]
	} else {
		_, self_name, _ := os.split_path(os.executable())
		// e.g. ['/path/to/', 'patch-d514b17f', '.exe']
		patch_id = self_name.all_after('patch-')
	}
	// validate patch id
	if patch_id.len == 8 {
		hex_strings := '0123456789abcdef'
		for ch in patch_id {
			if !hex_strings.contains_u8(ch) {
				panic('Invalid patch ID: ${patch_id}')
			}
		}
		return patch_id
	} else {
		panic('Invalid patch ID: ${patch_id}')
	}
}

fn locate_target_directory() !string {
	currdir := os.dir(os.executable())
	println('Current executable directory: ${currdir}')

	mut projdir := ''
	
	possible_projdir, possible_patch_dirname, _ := os.split_path(currdir)
	if
		possible_patch_dirname == 'patches' && 
		os.exists('${possible_projdir}/source')
	{
		// the most ideal case.
		projdir = possible_projdir.replace('\\', '/')
	}

	else if 
		os.exists('${currdir}/source') &&
		os.exists('${currdir}/python')
	{
		// user has put patch besides "source" directory.
		if !os.exists('${currdir}/patches') {
			os.mkdir('${currdir}/patches')!
		}
		projdir = currdir.replace('\\', '/')
	}

	else {
		// ask user to manually input project directory.
		println('Cannot locate project directory. Please input it manually.')
		println('Tip:')
		println('  To continue, input the absolute path of your application ' +
		        'root path.')
		println('  To exit, input "exit" or just close the console window.')

		// https://docs.vlang.io/statements-&-expressions.html#bare-for
		for {
			projdir = os.input('Project directory: ')
			if projdir == '' {
				continue
			} else if projdir == 'exit' {
				panic('Exit.')
			} else if 
				projdir != '' &&
				os.exists('${projdir}/source') &&
				os.exists('${projdir}/python')
			{
				break
			} else {
				println('Invalid project directory! Please try again.')
			}
		}

		projdir = projdir.replace('\\', '/')
		if !os.exists('${projdir}/patches') {
			os.mkdir('${projdir}/patches')!
		}
	}

	println('Project directory: ${projdir}')
	return projdir
}

fn parse_arguments() (bool, bool) {
	args := arguments()[1..]
	dry_run := '-d' in args || '--debug' in args || '--dry-run' in args
	verbose := '-v' in args || '--verbose' in args
	return dry_run, verbose
}

fn save_record(patch_id string, patch_folder string) ! {
	file := '${patch_folder}/patch_history.txt'
	if os.exists(file) {
		old := os.read_file(file)!
		new := '${patch_id}\n${old}'
		os.write_file(file, new)!
	} else {
		os.write_file(file, patch_id)!
	}
}
