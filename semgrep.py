import re

def normalize_line(line):
    return re.sub(r'(\d+\.\d+\.\d+)_(pure|patched)', r'\1_XXXX', line)

def read_and_process(filename):
    with open(filename, 'r') as f:
        return [normalize_line(line) for line in f]

def compare_reports(pure_lines, patched_lines):
    pure_set = set(pure_lines)
    patched_set = set(patched_lines)
    
    common = [line for line in pure_lines if line in patched_set]
    pure_only = [line for line in pure_lines if line not in patched_set]
    patched_only = [line for line in patched_lines if line not in pure_set]
    
    return common, pure_only, patched_only

def write_output(filename, lines):
    """将结果写入文件"""
    with open(filename, 'w') as f:
        f.writelines(lines)

def main():
    pure_entries = read_and_process('apparmor-2.13.3_pure_semgrep_converted.txt')
    patched_entries = read_and_process('apparmor-2.13.3_patched_semgrep_converted.txt')
    
    common, pure_only, patched_only = compare_reports(pure_entries, patched_entries)
    
    write_output('common_semgrep.txt', common)
    write_output('pure_only_semgrep.txt', pure_only)
    write_output('patched_only_semgrep.txt', patched_only)

if __name__ == "__main__":
    main()