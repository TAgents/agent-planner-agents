#!/usr/bin/env python3
import os
import stat
import datetime
import argparse

# Directories you want to exclude from the context (e.g. virtual environments or output folders)
EXCLUDE_DIRS = {'.venv', 'outputs', 'logs'}

# Predefined files to exclude
EXCLUDE_FILES = {".env,createLLMContext.py"}

# Output markdown filename
OUTPUT_MD = "project_context.md"

def is_text_file(filepath):
    """
    Check if a file is likely to be text by trying to read a small portion.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except Exception:
        return False

def get_file_metadata(filepath):
    """
    Retrieve file metadata such as size, last modified time, and permissions.
    """
    st = os.stat(filepath)
    size = st.st_size
    mod_time = datetime.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    permissions = stat.filemode(st.st_mode)
    return size, mod_time, permissions

def write_file_entry(md_file, rel_path):
    """
    Write a markdown entry for a given file, including its metadata and contents.
    """
    size, mod_time, permissions = get_file_metadata(rel_path)
    header = f"### {rel_path}\n"
    meta = (f"**Metadata:**\n"
            f"- **Size:** {size} bytes\n"
            f"- **Last Modified:** {mod_time}\n"
            f"- **Permissions:** {permissions}\n\n")
    md_file.write(header)
    md_file.write(meta)
    
    # If it's a text file, try to read its contents.
    if is_text_file(rel_path):
        try:
            with open(rel_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"
    else:
        content = "*Non-text or binary file content not included.*"
    
    md_file.write("**Contents:**\n")
    md_file.write("```text\n")
    md_file.write(content)
    md_file.write("\n```\n\n")

def generate_markdown_context(root_dir="."):
    """
    Walk through the project directory and write all relevant file info into a markdown file.
    """
    with open(OUTPUT_MD, 'w', encoding='utf-8') as md_file:
        md_file.write("# Project File Context\n\n")
        md_file.write("This file was generated to provide context to an LLM about the project codebase.\n\n")
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip any directories in the exclude list
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for filename in filenames:
                # Skip files that are in the exclude list
                if filename in EXCLUDE_FILES:
                    continue
                # Construct the full relative path of the file
                rel_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                # Write the file entry to markdown
                write_file_entry(md_file, rel_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate markdown context for project codebase.")
    parser.add_argument(
        "--exclude-files", 
        nargs="*", 
        default=[], 
        help="Additional file names to exclude (e.g., mcp_agent.config.yaml)"
    )
    args = parser.parse_args()

    # Update the excluded files set with any additional files passed via command-line.
    EXCLUDE_FILES.update(args.exclude_files)

    generate_markdown_context()
    print(f"Markdown context file '{OUTPUT_MD}' has been generated.")
