// download all resources from a given URL.
// the URL is passed by `os.args`.
import os

fn main() {
	url := get_url()
	println(url)
	// table of resources
	// <url>
	// |- depsland.zip
}

fn get_url() string {
	// println(os.args)
	if os.args.len > 1 {
		return os.args[1]
	} else {
		return 'http://172.20.128.105:2184' // TEST
	}
}
