"""Portable, standard-library tooling. Never execute notebooks or contact services."""
from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path
import re
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENTS = {"dev", "uat", "prod"}
SECRET_NAMES = {
    "ACCESS_KEY", "SECRET_KEY", "ACCESS_KEY1", "SECRET_KEY1", "WXD_HMS_PASSWORD",
    "HIVE_TRUSTSTORE_PASSWORD", "HRM_TOKEN", "VLP_SIGN_SECRET",
}
S3_PUBLIC = {"S3_ENDPOINT", "BUCKET_NAME"}
BRONZE_PUBLIC = {
    "BUCKET_NAME1", "WXD_HMS_USERNAME", "HIVEMETASTORE_HOST", "HIVE_TRUSTSTORE_PATH",
    "WXD_INSTANCE_ID", "HADOOP_AMS_URL", "HADOOP_CAS_ENDPOINT", "HADOOP_CPG_ENDPOINT",
}
BRONZE_SECRETS = {"WXD_HMS_PASSWORD", "HIVE_TRUSTSTORE_PASSWORD"}
EXCLUDED_DIRS = {".local", ".git", ".venv", "__pycache__", ".ipynb_checkpoints", "dist"}


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        # Do not expose the contents of a malformed credentials file.
        raise ValueError(f"Cannot read JSON file: {Path(path).name}") from None


def source_files(root=ROOT):
    """One shared source-only selection for scanning and packaging."""
    for path in sorted(Path(root).rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Symlink is not allowed in source package: {relative}")
        if not path.is_file():
            continue
        if relative.parts[:2] == ("config", "secrets") and path.name not in {"secrets.example.json", "README.md"}:
            continue
        if path.name.endswith(".local.json") or path.name.startswith(".env") or path.name == ".DS_Store":
            continue
        if path.suffix.lower() in {".pem", ".key", ".p12", ".jks", ".log", ".pyc", ".zip"}:
            continue
        yield path


def _present(value):
    return isinstance(value, str) and bool(value.strip()) and not value.startswith(("<", "${"))


def job_environment(environment, layer, source, object_name, etl_date=None,
                    date_from=None, date_to=None, root=ROOT):
    root = Path(root)
    if environment not in ENVIRONMENTS:
        raise ValueError("Environment must be dev, uat or prod")
    manifest = read_json(root / "pipeline_manifest.json")
    entries = [entry for entry in manifest["notebooks"]
               if (entry["layer"], entry["source"], entry["object"]) == (layer, source, object_name)]
    if len(entries) != 1 or entries[0]["status"] != "implementation_present_runtime_unverified":
        raise ValueError("No deployable implementation for this layer/source/object; draft is not a job")
    if layer not in {"landing", "bronze"}:
        raise ValueError("Job generation currently supports Landing and Bronze only")
    if (date_from or date_to) and (source, layer) != ("vlp", "landing"):
        raise ValueError("Date window overrides are implemented only for VLP Landing")
    batch = etl_date or (datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date() - timedelta(days=1)).isoformat()
    try:
        if date.fromisoformat(batch).isoformat() != batch:
            raise ValueError()
        for boundary in (date_from, date_to):
            if boundary and date.fromisoformat(boundary).isoformat() != boundary:
                raise ValueError()
        if (date_from or date_to) and not (date_from and date_to and date_from < date_to):
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("Use YYYY-MM-DD; VLP window needs both boundaries with date_from < date_to") from None

    profile = read_json(root / "config" / "environments" / f"{environment}.json")
    private = read_json(root / "config" / "secrets" / f"{environment}.local.json")
    if profile.get("environment") != environment or private.get("environment") != environment:
        raise ValueError("Environment label mismatch between selected profile and secrets")
    public, secrets = profile["variables"], private["values"]
    if SECRET_NAMES.intersection(public):
        raise ValueError("Secret variables must not be stored in a public environment profile")
    if set(secrets) - SECRET_NAMES:
        raise ValueError("Unknown names in secrets file; use credentials.catalog.json")
    public_names = set(S3_PUBLIC)
    secret_names = {"ACCESS_KEY", "SECRET_KEY"}
    if layer == "bronze":
        public_names |= BRONZE_PUBLIC
        secret_names |= BRONZE_SECRETS
    elif source == "hrm":
        public_names.add("HRM_BASE_URL")
        secret_names.add("HRM_TOKEN")
    elif source == "vlp":
        public_names.add("VLP_URL")
        secret_names.add("VLP_SIGN_SECRET")
    missing = sorted(name for name in public_names if not _present(public.get(name)))
    missing += sorted(name for name in secret_names if not _present(secrets.get(name)))
    if missing:
        raise ValueError("Missing configured names: " + ", ".join(missing))
    catalog = profile["catalogs"]["bronze"]
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalog):
        raise ValueError("Invalid Bronze catalog identifier")
    values = {name: public[name] for name in sorted(public_names)}
    values.update({name: secrets[name] for name in sorted(secret_names)})
    if layer == "bronze":
        for name in ("ACCESS_KEY1", "SECRET_KEY1"):
            if _present(secrets.get(name)):
                values[name] = secrets[name]
    values.update({
        "PIPELINE_ENV": environment, "ETL_Date": batch, "ICEBERG_CATALOG1": catalog,
        "TABLE_NAME": f"{catalog}.{source}.{object_name}",
        "SOURCE_NAME": f"{source}.api.{object_name}" if layer == "landing"
                       else f"s3://{public['BUCKET_NAME']}/{source}/{object_name}/{batch.replace('-', '')}",
        "LOG_TABLE": f"{catalog}.pipeline.log_pipeline",
    })
    if layer == "landing":
        options = profile.get("source_options", {}).get(source, {})
        allowed_options = {
            "hrm": {"HRM_PAGE_PARAM", "HRM_SIZE_PARAM", "HRM_PAGE_SIZE", "HRM_MAX_PAGES", "HRM_CA_BUNDLE"},
            "vlp": {"VLP_PAGE_SIZE", "VLP_MAX_PAGES", "VLP_REQUESTS_PER_SECOND", "VLP_TIME_UNIT", "VLP_CA_BUNDLE"},
        }
        if set(options) - allowed_options[source]:
            raise ValueError("Unknown source options; environment/credentials cannot be overridden here")
        values.update(options)
    if date_from:
        values.update(VLP_DATE_FROM=date_from, VLP_DATE_TO=date_to)
    for name, value in values.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) or not isinstance(value, str) or any(ch in value for ch in "\r\n\x00"):
            raise ValueError("Job variables must have valid names and single-line string values")
    return values


def write_job_environment(values, path, root=ROOT):
    allowed = (Path(root) / ".local").resolve()
    destination = Path(path).resolve()
    try:
        destination.relative_to(allowed)
    except ValueError:
        raise ValueError("Write generated credentials only under .local/") from None
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".job-", dir=destination.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write("".join(f"{name}={value}\n" for name, value in sorted(values.items())))
        os.chmod(temporary, 0o600)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return destination
