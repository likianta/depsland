import json
import os
import regex

struct Metadata {
	appid   string
	relpath string
mut:
	version string
}

struct Version {
	major    int
	minor    int
	patch    int
	pre_code string
	pre_num  int
}

fn main() {
	// get current dir
	curr_dir := os.dir(os.executable())
	println(curr_dir)

	embed := $embed_file('_readme_meta.json')
	// println(embed.to_string())
	data := json.decode(Metadata, embed.to_string())!
	println(data)

	// path: string
	mut relpath := ''
	if data.version == '*' {
		// println(data.relpath.split('/<version>'))
		reldir := data.relpath
			.split('/<version>')[0]
			.replace('<appid>', data.appid)
		absdir := os.join_path_single(curr_dir, reldir)
		// println(dir)
		mut versions := os.ls(absdir)!
		versions = versions.filter(it != '.inst_history')
		if versions.len > 1 {
			versions.sort_with_compare(compare_version)
		}
		// println(versions)
		best_version := versions.pop()
		relpath = data.relpath
			.replace('<appid>', data.appid)
			.replace('<version>', best_version)
	} else {
		relpath = data.relpath
			.replace('<appid>', data.appid)
			.replace('<version>', data.version)
	}
	println(relpath)

	abspath := os.join_path_single(curr_dir, relpath)
	os.execute_or_panic(abspath)
}

fn compare_version(a &string, b &string) int {
	a_ver := normalize_version(a) or { panic(a) }
	b_ver := normalize_version(b) or { panic(b) }
	if a_ver.major < b_ver.major {
		return -1
	} else if a_ver.major > b_ver.major {
		return 1
	}
	if a_ver.minor < b_ver.minor {
		return -1
	} else if a_ver.minor > b_ver.minor {
		return 1
	}
	if a_ver.patch < b_ver.patch {
		return -1
	} else if a_ver.patch > b_ver.patch {
		return 1
	}
	if a_ver.pre_code < b_ver.pre_code {
		return -1
	} else if a_ver.pre_code > b_ver.pre_code {
		return 1
	}
	return 0
}

fn normalize_version(ver string) !Version {
	re := regex.regex_opt(r'(\d+)\.(\d+)\.(\d+)(?:([ab])(\d+))?')!
	re.match_string(ver)
	mut elements := ungroup_string(ver, re.get_group_list())
	if elements.len == 3 {
		elements << ['z', '0']
	}
	return Version{
		major:    elements[0].int()
		minor:    elements[1].int()
		patch:    elements[2].int()
		pre_code: elements[3]
		pre_num:  elements[4].int()
	}
}

fn ungroup_string(s string, groups []regex.Re_group) []string {
	mut out := []string{}
	for grp in groups {
		if grp.start == -1 {
			break
		}
		out << s[grp.start..grp.end]
	}
	return out
}
