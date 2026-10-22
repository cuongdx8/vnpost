"""Validate portable source, notebook syntax, inventory and credential separation."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from repository_tools import ROOT, SECRET_NAMES, read_json, source_files


def validate(root=ROOT):
    root = Path(root)
    errors = []
    files = list(source_files(root))
    known = set()
    for path in (root / "config" / "secrets").glob("*.local.json"):
        known.update(value for value in read_json(path).get("values", {}).values()
                     if isinstance(value, str) and value)
    manifest = read_json(root / "pipeline_manifest.json")
    entries = {entry["path"]: entry for entry in manifest["notebooks"]}
    notebook_count, cell_count = 0, 0

    def inspect_code(code, relative):
        nonlocal cell_count
        try:
            tree = ast.parse(code)
        except SyntaxError:
            errors.append(f"Invalid Python syntax: {relative}")
            return
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("getenv", "setdefault") and len(node.args) > 1:
                key, default = node.args[:2]
                if isinstance(key, ast.Constant) and key.value in SECRET_NAMES and isinstance(default, ast.Constant) and default.value:
                    errors.append(f"Nonempty credential default: {relative} ({key.value})")
            if isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value in SECRET_NAMES and isinstance(value, ast.Constant) and value.value:
                        errors.append(f"Hardcoded credential dictionary: {relative} ({key.value})")
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and node.value.value:
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in SECRET_NAMES:
                        errors.append(f"Hardcoded credential assignment: {relative} ({target.id})")

    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"Unexpected binary in source: {relative}")
            continue
        if any(value in text for value in known):
            errors.append(f"Local credential value found in source: {relative}")
        if ("/" + "Users/") in text or ("/private" + "/tmp/") in text:
            errors.append(f"Machine-specific absolute path in source: {relative}")
        if path.suffix == ".py":
            inspect_code(text, relative)
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if target.startswith(("http:", "https:", "#")):
                    continue
                target = target.split("#", 1)[0]
                if target and not (path.parent / target).exists():
                    errors.append(f"Broken Markdown link: {relative} -> {target}")
        if path.suffix == ".ipynb":
            notebook_count += 1
            notebook = json.loads(text)
            entry = entries.get(relative)
            if not entry or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                errors.append(f"Missing/stale inventory hash: {relative}")
            count = 0
            for cell in notebook["cells"]:
                if cell["cell_type"] != "code":
                    continue
                count += 1
                cell_count += 1
                if cell.get("outputs") or cell.get("execution_count") is not None:
                    errors.append(f"Saved execution output/count: {relative}")
                inspect_code("".join(cell["source"]), relative)
            if entry and count != entry["code_cell_count"]:
                errors.append(f"Stale code cell count: {relative}")
    for relative, entry in entries.items():
        if not (root / relative).is_file():
            errors.append(f"Missing notebook: {relative}")
        for dependency in entry.get("depends_on", []):
            if dependency not in entries:
                errors.append(f"Missing dependency: {relative}")
    for name in ("dev", "uat", "prod"):
        profile = read_json(root / "config" / "environments" / f"{name}.json")
        if profile["environment"] != name or SECRET_NAMES.intersection(profile["variables"]):
            errors.append(f"Invalid public profile separation: {name}")
    return errors, {"source_files": len(files), "notebooks": notebook_count, "code_cells": cell_count,
                    "local_credential_values_checked": len(known), "actual_service_execution": False}


def main():
    try:
        errors, summary = validate()
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Repository validation failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(json.dumps({"status": "PASS", **summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
