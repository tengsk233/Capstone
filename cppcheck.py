import re

def normalize_path(line):
    return re.sub(r'(\d+  \.  \d+  \.  \d+  )  _  (pure|patched)', r'\1_XXXX', line)

def read_entries(filename):
    with open(filename, 'r') as f:
        return [normalize_path(line) for line in f]

def compare_results(pure_entries, patched_entries):
    pure_set = set(pure_entries)
    patched_set = set(patched_entries)
    
    common = [line for line in pure_entries if line in patched_set]
    pure_only = [line for line in pure_entries if line not in patched_set]
    patched_only = [line for line in patched_entries if line not in pure_set]
    
    return common, pure_only, patched_only

def write_output(filename, entries):
    """写入结果文件"""
    with open(filename, 'w') as f:
        f.writelines(entries)

def main():
    pure_entries = read_entries('apparmor-2.13.3_pure_cppcheck_converted.txt')
    patched_entries = read_entries('apparmor-2.13.3_patched_cppcheck_converted.txt')
    
    common, pure_only, patched_only = compare_results(pure_entries, patched_entries)
    
    write_output('common_cppcheck.txt', common)
    write_output('pure_only_cppcheck.txt', pure_only)
    write_output('patched_only_cppcheck.txt', patched_only)

if __name__ == "__main__":
    main()