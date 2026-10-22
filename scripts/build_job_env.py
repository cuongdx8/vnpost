"""Generate CP4D NAME=value lines locally; never print credentials or run a job."""
import argparse
from pathlib import Path
import sys
from repository_tools import ROOT, job_environment, write_job_environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", choices=("dev", "uat", "prod"), required=True)
    parser.add_argument("--layer", choices=("landing", "bronze"), required=True)
    parser.add_argument("--source", choices=("hrm", "vlp"), required=True)
    parser.add_argument("--object", dest="object_name", required=True)
    parser.add_argument("--etl-date")
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Validate and print names only")
    args = parser.parse_args()
    try:
        values = job_environment(args.environment, args.layer, args.source, args.object_name,
                                 args.etl_date, args.date_from, args.date_to)
        if args.dry_run:
            print("Valid configuration; variable names only: " + ", ".join(sorted(values)))
        else:
            output = args.output or ROOT / ".local" / "jobs" / args.environment / f"{args.layer}.{args.source}.{args.object_name}.env"
            destination = write_job_environment(values, output)
            print(f"Created private CP4D job environment file: {destination}")
            print("Credentials were not printed. This command did not call API/S3/Spark or run a notebook.")
    except (ValueError, KeyError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
