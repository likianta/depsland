import compress.szip
import json
import os

fn main() {
	dry_run := parse_arguments()

	patch_id := '<PATCH_ID>'

    currdir := os.dir(os.executable())
    println('Current executable directory: ${currdir}')
	projdir, currdirname, _ := os.split_path(currdir)
	root_i := '${currdir}/${patch_id}'.replace('\\', '/')
	root_o := '${projdir}/source'.replace('\\', '/')
	
	if !dry_run {
		if currdirname != 'patches' {
			panic('You must place this file in "patches" directory.')
		}
		if !os.exists('${projdir}/source') {
			panic('Cannot find "source" directory.')
		}
	}

	assets_map_data := $embed_file('../grocery/assets_map.json')
	assets_zip_data := $embed_file('../grocery/assets.zip')
	
	// prepare resources
	if dry_run {
		if !os.exists(root_i) { os.mkdir(root_i)! }
		if !os.exists('${root_i}/backups') { os.mkdir('${root_i}/backups')! }
		os.write_bytes('${root_i}/assets_map.json', assets_map_data.to_bytes())!
		os.write_bytes('${root_i}/assets.zip', assets_zip_data.to_bytes())!
		szip.extract_zip_to_dir('${root_i}/assets.zip', root_i)!
	} else {
		if os.exists(root_i) { os.rmdir_all(root_i)! }
		os.mkdir(root_i)!
		os.mkdir('${root_i}/backups')!
		os.write_bytes('${root_i}/assets_map.json', assets_map_data.to_bytes())!
		os.write_bytes('${root_i}/assets.zip', assets_zip_data.to_bytes())!
		szip.extract_zip_to_dir('${root_i}/assets.zip', root_i)!
		assert os.exists('${root_i}/assets')
	}

	assets_map := json.decode(
		map[string]string, assets_map_data.to_string()
	)!

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

		file_i = '${root_i}/${file_id}'
		file_m = '${root_i}/backups/${file_id}'
		file_o = '${root_o}/${relpath}'
		
		if dry_run {
			if do_append {
				if os.exists(file_o) {
					println('[dry_run] Update "source/${relpath}" (${file_id})')
				} else {
					println('[dry_run] Append "source/${relpath}" (${file_id})')
				}
			} else {
				println('[dry_run] Delete "source/${relpath}" (${file_id})')
			}
		} else {
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

fn parse_arguments() bool {
	args := arguments()[1..]
	dry_run := '-d' in args || '--debug' in args || '--dry-run' in args
	return dry_run
}
