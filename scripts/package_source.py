"""Build a source-only ZIP; private credentials and handoff files are excluded."""
import argparse
from pathlib import Path
import zipfile
from repository_tools import ROOT, source_files
from validate_repository import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "vnpost-data-pipeline-source.zip")
    args = parser.parse_args()
    errors, _ = validate()
    if errors:
        raise SystemExit("Source validation failed; run scripts/validate_repository.py")
    output = args.output.resolve()
    if output.suffix != ".zip" or output == ROOT:
        raise SystemExit("Output must be a .zip file")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in source_files():
            if path.resolve() != output:
                archive.write(path, "vnpost-data-pipeline/" + path.relative_to(ROOT).as_posix())
    print(f"Created source-only archive: {output}")
    print("No local credentials, private handoff, generated job files or notebook outputs included.")


if __name__ == "__main__":
    main()
