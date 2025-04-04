import re

def normalize_path(line):
    return re.sub(r'_pure|_patched', '_XXXX', line)

def read_and_normalize(filename):
    with open(filename, 'r') as f:
        return [normalize_path(line) for line in f]

def main():
    pure_lines = read_and_normalize('apparmor-2.13.3_pure_clang-tidy_converted.txt')
    patched_lines = read_and_normalize('apparmor-2.13.3_patched_clang-tidy_converted.txt')
    
    patched_set = set(patched_lines)
    
    common = []
    pure_only = []
    for line in pure_lines:
        if line in patched_set:
            common.append(line)
        else:
            pure_only.append(line)
    
    patched_only = [line for line in patched_lines if line not in common]
    
    with open('clang-tidy-common.txt', 'w') as f:
        f.writelines(common)
    
    with open('clang-tidy-pure_only.txt', 'w') as f:
        f.writelines(pure_only)
    
    with open('clang-tidy-patched_only.txt', 'w') as f:
        f.writelines(patched_only)

if __name__ == "__main__":
    main()