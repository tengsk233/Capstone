import re
from collections import Counter

def count_cwe_in_file(filename):
    print(f"Processing file: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"File length: {len(content)} characters")
    print("-" * 40)
    
    cwe_numbers = re.findall(r'CWE-(\d+)', content)
    cwe_codes = [f"CWE-{num}" for num in cwe_numbers]
    
    unique_cwe = set(cwe_codes)
    print("find CWE code：", unique_cwe)
    print("total {} different CWE".format(len(unique_cwe)))
    
    counts = Counter(cwe_codes)
    print("\neach CWE count：")
    for code, cnt in counts.items():
        print(f"{code}: {cnt}")

if __name__ == "__main__":
    print("Starting countCWE...")
    print("pure only")
    count_cwe_in_file(r"C:\Users\Sikai Teng\Desktop\result\curl\curl_res\flawfinder-pure_only.txt")
    print("-" * 40)
    print("patched only")
    count_cwe_in_file(r"C:\Users\Sikai Teng\Desktop\result\curl\curl_res\flawfinder-patched_only.txt")
    print("-" * 40)

    print("commen")
    count_cwe_in_file(r"C:\Users\Sikai Teng\Desktop\result\curl\curl_res\flawfinder-common.txt")
    print("-" * 40)

