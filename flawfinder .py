import re

def normalize_path(line):
    return re.sub(r'(\d+\.\d+\.\d+)_(pure|patched)', r'\1_XXXX', line)

def read_entries(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    entries = []
    for i in range(0, len(lines), 2):
        if i+1 < len(lines):
            entry = normalize_path(lines[i]) + lines[i+1]
        else:
            entry = normalize_path(lines[i])
        entries.append(entry)
    return entries

def compare_entries(pure_entries, patched_entries):
    pure_set = set(pure_entries)
    patched_set = set(patched_entries)
    
    common = [entry for entry in pure_entries if entry in patched_set]
    pure_only = [entry for entry in pure_entries if entry not in patched_set]
    patched_only = [entry for entry in patched_entries if entry not in pure_set]
    
    return common, pure_only, patched_only

def write_output(filename, entries):
    with open(filename, 'w') as f:
        for entry in entries:
            f.write(entry)

def main():
    pure_entries = read_entries('apparmor-2.13.3_pure_flawfinder_converted.txt')
    patched_entries = read_entries('apparmor-2.13.3_patched_flawfinder_converted.txt')
    
    common, pure_only, patched_only = compare_entries(pure_entries, patched_entries)
    
    write_output('flawfinder-common.txt', common)
    write_output('flawfinder-pure_only.txt', pure_only)
    write_output('flawfinder-patched_only.txt', patched_only)

if __name__ == "__main__":
    main()