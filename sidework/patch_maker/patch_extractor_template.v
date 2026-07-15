import compress.szip
import json
import os

fn main() {
	patch_id := '<PATCH_ID>'

	assets_map_data := $embed_file('grocery/assets_map.json')
	assets_zip_data := $embed_file('grocery/assets.zip')
	
	root_i := './${patch_id}'
	root_o := '../source'

	// prepare resources
	if os.exists(root_i) { os.rmdir_all(root_i)! }
	os.mkdir(root_i)!
	os.mkdir('${root_i}/backups')!
	os.write_bytes('${root_i}/assets_map.json', assets_map_data)!
	os.write_bytes('${root_i}/assets.zip', assets_zip_data)!
	szip.extract_zip_to_dir('${root_i}/assets.zip', root_i)!
	assert os.exists('${root_i}/assets')

	assets_map := json.decode(
		map[string]string, assets_map_data.to_string()
	)!

	// apply patch
	mut relpath := ''
	mut flag_pos := 0
	mut flag := '0'
	mut file_i := ''
	mut file_m := ''
	mut file_o := ''
	for file_id, value in assets_map {
		println('${value} (${file_id})')

		flag_pos = value.last_index(':')!
		relpath = value[..flag_pos]
		flag = value[flag_pos + 1..]

		file_i = '${root_i}/${file_id}'
		file_m = '${root_i}/backups/${file_id}'
		file_o = '${root_o}/${relpath}'
		
		if flag == '1' {
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
