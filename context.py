#!/usr/bin/env python3

import subprocess
import os
from treelib import Tree
import pyperclip
import ast
import re
import json

FILE_COUNT = 20
LINE_COUNT = 20

SUPPORTED_EXTENSIONS = [
    ".py",
    ".go",
    ".js",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".rb",
    ".php",
    ".jsx",
    ".svelte",
    ".md",
    ".zig",
]

PROMPT = """
I am using you as a prompt generator. I've dumped the entire context of my code base, and I have a specific problem. Please come up with a proposal to my problem - including the code and general approach.


<Problem>


Please make sure that you leave no details out and follow my requirements specifically. I know what I am doing, and you can assume that there is a reason for my arbitrary requirements. 

When generating the full prompt with all of the details, keep in mind that the model you are sending this to is not as intelligent as you. It is great at very specific instructions, so please stress that they are just that: specific. 

Come up with discrete steps such that the worse LLM I am passing this to can build intermediately; as to keep it on the rails. Make sure to stress that it stops for feedback at each discrete step.
"""


def parse_requirements(file_path):
    """Parse requirements.txt and extract package names."""
    with open(file_path, "r") as f:
        lines = f.readlines()
    packages = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):  # Ignore empty lines and comments
            # Extract package name before any version specifiers
            pkg = re.split(r"[=<>!~\s]", line)[0]
            packages.append(pkg)
    return packages


def parse_package_json(file_path):
    """Parse package.json and extract dependency names."""
    with open(file_path, "r") as f:
        data = json.load(f)
    deps = []
    if "dependencies" in data:
        deps.extend(data["dependencies"].keys())
    if "devDependencies" in data:
        deps.extend(data["devDependencies"].keys())
    return deps


def parse_cargo_toml(file_path):
    """Parse Cargo.toml and extract dependency names."""
    with open(file_path, "r") as f:
        content = f.read()
    # Find the [dependencies] section
    deps_section = re.search(r"\[dependencies\]\s*(.*?)(?=\[|\Z)", content, re.DOTALL)
    if deps_section:
        deps_content = deps_section.group(1)
        # Extract crate names, ignoring versions and other details
        crates = re.findall(r"^\s*(\w[\w-]*)", deps_content, re.MULTILINE)
        return crates
    return []


def parse_go_mod(file_path):
    """Parse go.mod and extract module names."""
    with open(file_path, "r") as f:
        content = f.read()
    requires = re.findall(r"require\s+(\S+)", content)
    blocks = re.findall(r"require\s*\((.*?)\)", content, re.DOTALL)
    for block in blocks:
        lines = block.splitlines()
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split()
                if parts:
                    requires.append(parts[0])
    return requires


def get_dependencies():
    """Get a simplified list of dependency names."""
    dep_files = {
        "Cargo.toml": ("Rust", parse_cargo_toml),
        "package.json": ("JavaScript/TypeScript", parse_package_json),
        "go.mod": ("Go", parse_go_mod),
        "requirements.txt": ("Python", parse_requirements),
    }

    deps_by_category = {}
    for dep_file, (category, parser) in dep_files.items():
        path = os.path.join(get_git_root(), dep_file)
        if os.path.exists(path):
            try:
                dependencies = parser(path)
                if dependencies:
                    deps_by_category[category] = dependencies
            except Exception as e:
                print(f"Error parsing {dep_file}: {e}")
    if not deps_by_category:
        return ""
    output = ""
    for category, dependencies in deps_by_category.items():
        output += f"**{category}**:\n"
        for dep in dependencies:
            output += f"- {dep}\n"
        output += "\n"
    return output.strip()


def is_source_file(file):
    """Check if a file is a source file based on its extension."""
    return any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS)


def extract_js_ts_symbols(file_path):
    """Enhanced JS/TS parsing for configs, utilities, and exports."""
    docstring = ""
    symbols = []
    with open(file_path, "r", errors="ignore") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):  # Scan full file
            stripped = line.strip()
            # Collect comments as docstring
            if re.match(r"^//", stripped) or re.match(r"^/\*", stripped):
                docstring += line.strip() + "\n"
            # Match functions (including export function)
            elif re.match(
                r"^(export\s+)?function\s+\w+|const\s+\w+\s*=\s*\(.*\)\s*=>|async\s+(export\s+)?function\s+\w+",
                stripped,
            ):
                func_match = re.search(
                    r"(?:export\s+)?function\s+(\w+)|const\s+(\w+)\s*=", stripped
                )
                if func_match:
                    name = func_match.group(1) or func_match.group(2)
                    symbols.append(f"Function: {name}")
            # Match classes
            elif re.match(r"^class\s+\w+", stripped):
                class_name = re.search(r"class\s+(\w+)", stripped).group(1)
                symbols.append(f"Class: {class_name}")
            # Match exports
            elif re.match(r"^export\s+(default\s+)?[{a-zA-Z]", stripped):
                export_name = re.search(r"export\s+(default\s+)?(\w+)", stripped)
                if export_name and export_name.group(2):
                    symbols.append(f"Export: {export_name.group(2)}")
            # Match top-level variables
            elif re.match(r"^\w+\s*=", stripped):
                var_name = re.search(r"^\w+", stripped).group(0)
                symbols.append(f"Variable: {var_name}")

    # Construct output
    docstring_text = f"Docstring:\n{docstring.strip()}\n" if docstring else ""
    symbols_text = "Symbols:\n" + "\n".join(symbols) if symbols else ""
    # Fallback: if no symbols or docstring, show first 10 lines
    if not (docstring or symbols):
        try:
            with open(file_path, "r", errors="ignore") as f:
                return "".join(f.readlines()[:10])
        except Exception as e:
            print(f"Error reading {file_path} in fallback: {e}")
            return f"Error: {e}"
    return docstring_text + symbols_text


def extract_go_symbols(file_path):
    """Extract package documentation and top-level symbols from Go files."""
    docstring = ""
    symbols = []
    with open(file_path, "r", errors="ignore") as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            if re.match(r"^//\s*Package", line) or re.match(r"^//\s+", line):
                docstring += line.strip() + "\n"
            elif re.match(r"^func\s+\w+", line):
                func_name = re.search(r"^func\s+(\w+)", line).group(1)
                symbols.append(f"Function: {func_name}")
            elif re.match(r"^type\s+\w+", line):
                type_name = re.search(r"^type\s+(\w+)", line).group(1)
                symbols.append(f"Type: {type_name}")
    docstring_text = f"Docstring:\n{docstring.strip()}\n" if docstring else ""
    symbols_text = "Symbols:\n" + "\n".join(symbols) if symbols else ""
    return docstring_text + symbols_text


def extract_header(file_path, lines=10):
    """Extract more lines or detailed info based on file type."""
    if file_path.endswith(".py"):
        try:
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
            docstring = ast.get_docstring(tree)
            symbols = []
            for node in tree.body[:10]:  # Get more top-level definitions
                if isinstance(node, ast.FunctionDef):
                    symbols.append(f"Function: {node.name}")
                elif isinstance(node, ast.ClassDef):
                    symbols.append(f"Class: {node.name}")
            docstring_text = f"Docstring: {docstring}\n" if docstring else ""
            symbols_text = "Symbols:\n" + "\n".join(symbols) if symbols else ""
            return docstring_text + symbols_text
        except Exception:
            pass
    elif file_path.endswith(".go"):
        return extract_go_symbols(file_path)
    elif file_path.endswith((".js", ".ts", ".tsx")):
        return extract_js_ts_symbols(file_path)
    try:
        with open(file_path, "r", errors="ignore") as f:
            return "".join(f.readlines()[:lines])
    except Exception:
        return "Unable to read file."


def get_git_root():
    """Get the root directory of the Git repository."""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Not inside a Git repository.")


def get_readme():
    """Read the contents of README.md if it exists."""
    readme_path = os.path.join(get_git_root(), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            return f.read()
    return None


def get_recent_commits(n=5):
    """Get the last N commit messages."""
    try:
        return (
            subprocess.check_output(["git", "log", "-n", str(n), "--pretty=format:%s"])
            .decode()
            .splitlines()
        )
    except subprocess.CalledProcessError:
        return []


def build_directory_tree(files, max_depth=2):
    """Build a tree structure of the directory."""
    tree = Tree()
    tree.create_node(os.path.basename(get_git_root()), "root", data={"depth": 0})
    for file in files:
        parts = file.split("/")
        current = "root"
        depth = 0
        for part in parts:
            depth += 1
            if depth > max_depth:
                break
            node_id = f"{current}/{part}"
            if not tree.contains(node_id):
                tree.create_node(part, node_id, parent=current, data={"depth": depth})
            current = node_id
    return tree


def get_last_modified(file):
    """Get the last modification date of a file."""
    try:
        return (
            subprocess.check_output(
                ["git", "log", "-1", "--pretty=format:%ad", "--date=short", "--", file]
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        return "Unknown"


def get_key_files(n=20):
    """Get the top N most-modified current source files."""
    current_files = subprocess.check_output(["git", "ls-files"]).decode().splitlines()
    source_files = [f for f in current_files if is_source_file(f)]
    file_counts = [(file, get_commit_count(file)) for file in source_files]
    sorted_files = sorted(file_counts, key=lambda x: x[1], reverse=True)
    key_files = [file for file, _ in sorted_files[:n]]
    return key_files


def get_commit_count(file):
    """Get the number of commits that modified the file."""
    try:
        output = subprocess.check_output(
            ["git", "log", "--follow", "--pretty=format:%H", file],
            stderr=subprocess.DEVNULL,
        ).decode()
        return len(output.splitlines())
    except subprocess.CalledProcessError:
        return 0


def get_tracked_files():
    """List all tracked files in the Git repository."""
    return subprocess.check_output(["git", "ls-files"]).decode().splitlines()


def format_context():
    """Format all collected context into a Markdown string."""
    context = ["# Project Context\n"]

    # Directory Structure
    context.append("## Directory Structure\n")
    tree = build_directory_tree(get_tracked_files())
    context.append(tree.show(stdout=False) + "\n")

    context.append(f"## Key Files (Top {FILE_COUNT} Most Modified)\n")
    for file in get_key_files(n=FILE_COUNT):
        last_modified = get_last_modified(file)
        context.append(f"### {file} (last modified: {last_modified})\n")
        context.append("```\n")
        context.append(extract_header(os.path.join(get_git_root(), file)))
        context.append("\n```\n")

    # README
    readme = get_readme()
    if readme:
        context.append("## README\n")
        context.append(readme + "\n")

    # Dependencies
    deps = get_dependencies()
    if deps:
        context.append("## Dependencies\n")
        context.append(deps + "\n")

    # Recent Commits
    context.append("## Recent Commits\n")
    for commit in get_recent_commits():
        context.append(f"- {commit}\n")

    # Final Problem Prompt
    context.append(PROMPT)

    return "".join(context)


def main():
    """Main function to run the script."""
    try:
        context = format_context()
        pyperclip.copy(context)
        print("Context copied to clipboard.")
        print(f"\nTop {FILE_COUNT} files and expanded context generated successfully.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
