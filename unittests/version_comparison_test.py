from depsland.utils import compare_version

print(compare_version('2.4.1', '<', '2.5.0b18'))
print(compare_version('2.4.1', '>=', '2.5.0b18'))
