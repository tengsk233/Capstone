#!/usr/bin/env python3
import os
import json
import xml.etree.ElementTree as ET

def process_clang_tidy(input_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as fin:
        return fin.read()

def process_flawfinder(input_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as fin:
        return fin.read()

def process_cppcheck(input_path):
    try:
        tree = ET.parse(input_path)
    except ET.ParseError as e:
        print(f"XML 解析错误 {input_path}: {e}")
        return ""
    root = tree.getroot()
    messages = []
    for error in root.findall('.//error'):
        severity = error.attrib.get('severity', 'N/A')
        error_id = error.attrib.get('id', 'N/A')
        msg = error.attrib.get('msg', 'N/A')
        messages.append(f"{severity}: {error_id}: {msg}")
    return "\n".join(messages)

def process_semgrep(input_path):
    with open(input_path, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    messages = []
    for result in data.get('results', []):
        severity = result.get('severity', 'N/A')
        path = result.get('path', 'N/A')
        start_line = result.get('start', {}).get('line', 'N/A')
        extra = result.get('extra', {})
        message_text = extra.get('message', 'N/A')
        messages.append(f"{severity}: {path}: {start_line} - {message_text}")
    return "\n".join(messages)

def main():
   
    base_dir = r"C:\Users\Sikai Teng\Desktop\apparmor"
    output_dir = os.path.join(base_dir, "apparmor_res")
    os.makedirs(output_dir, exist_ok=True)

    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item.lower().startswith("apparmor"):
            project_name = item
            print(f"Processing project: {project_name}")
            files_to_process = {
                'clang-tidy.txt': process_clang_tidy,
                'flawfinder.txt': process_flawfinder,
                'cppcheck.xml': process_cppcheck,
                'semgrep.json': process_semgrep
            }
            for fname, processor in files_to_process.items():
                file_path = os.path.join(item_path, fname)
                if os.path.isfile(file_path):
                    try:
                        content = processor(file_path)
                        base, _ = os.path.splitext(fname)
                        out_fname = f"{project_name}_{base}_converted.txt"
                        out_path = os.path.join(output_dir, out_fname)
                        with open(out_path, 'w', encoding='utf-8') as fout:
                            fout.write(content)
                        print(f"  Processed {fname} -> {out_fname}")
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                else:
                    print(f"  {fname} not found in {item_path}")

if __name__ == "__main__":
    main()
