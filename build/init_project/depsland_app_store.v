import os

fn main() {
	curr_dir := os.dir(os.executable())
	python := os.join_path_single(curr_dir, 'source/python/pythonw.exe')
	os.chdir(os.join_path_single(curr_dir, 'source'))!
	os.execvp(python, ['-m', 'depsland', 'launch-gui'])!
}
