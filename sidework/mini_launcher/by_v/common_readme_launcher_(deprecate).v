// get target info by resolving self file name. for example if we started from
// "hello_world-v1.0.0-debug.exe", we get "hello_world" and "1.0.0" from the
// file name.
import os
import regex

fn main() {
	exe := os.executable()
	curr_name := os.file_name(exe)
	println('current exe name: "${curr_name}"')

	re := regex.regex_opt(r'^(\w+)-v(\d+\.\d+\.\d+(?:[ab]\d+)?)')!
	re.match_string(curr_name)
	grp := re.get_group_list()

	appid := curr_name[grp[0].start..grp[0].end]
	version := curr_name[grp[1].start..grp[1].end]
	println('appid: ${appid}; version: ${version}')
}
