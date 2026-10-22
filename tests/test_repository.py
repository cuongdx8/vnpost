"""Offline tests for configuration isolation and source packaging; never run ETL."""
import ast
from copy import deepcopy
from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from repository_tools import SECRET_NAMES, job_environment, source_files, write_job_environment
from validate_repository import validate


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "config" / "environments").mkdir(parents=True)
        (self.root / "config" / "secrets").mkdir()
        self.profile = json.loads((ROOT / "config" / "environments" / "dev.json").read_text())
        self.private = {
            "environment": "dev",
            "values": {name: f"offline-fixture-{index}" for index, name in enumerate(sorted(SECRET_NAMES))},
        }
        shutil.copyfile(ROOT / "pipeline_manifest.json", self.root / "pipeline_manifest.json")
        self.save()

    def save(self, environment="dev"):
        (self.root / "config" / "environments" / f"{environment}.json").write_text(json.dumps(self.profile))
        (self.root / "config" / "secrets" / f"{environment}.local.json").write_text(json.dumps(self.private))

    def build(self, layer="landing", source="hrm", object_name="unit", **kwargs):
        return job_environment("dev", layer, source, object_name, "2026-10-21", root=self.root, **kwargs)

    def test_all_six_jobs_and_notebook_configuration_cells(self):
        for source, object_name in (("hrm", "unit"), ("hrm", "employee"), ("vlp", "order_detail")):
            for layer in ("landing", "bronze"):
                with self.subTest(source=source, object=object_name, layer=layer):
                    values = self.build(layer, source, object_name)
                    self.assertEqual(values["PIPELINE_ENV"], "dev")
                    self.assertEqual(values["TABLE_NAME"], f"bronze.{source}.{object_name}")
                    self.assertEqual(values["ETL_Date"], "2026-10-21")
                    if layer == "bronze":
                        self.assertNotIn("HRM_TOKEN", values)
                        self.assertNotIn("VLP_SIGN_SECRET", values)
                    else:
                        self.assertNotIn("WXD_HMS_PASSWORD", values)
                    path = ROOT / "notebooks" / layer / source / f"NB_{layer}.{source}.{object_name}.ipynb"
                    notebook = json.loads(path.read_text())
                    config = next("".join(cell["source"]) for cell in notebook["cells"]
                                  if cell["cell_type"] == "code" and "S3_ENDPOINT =" in "".join(cell["source"]))
                    namespace = dict(os=os, re=re, datetime=datetime, timedelta=timedelta,
                                     date=date, ZoneInfo=ZoneInfo, uuid=uuid)
                    with patch.dict(os.environ, values, clear=True):
                        exec(compile(config, path.name, "exec"), namespace)
                    self.assertEqual(namespace["PIPELINE_ENV"], "dev")
                    self.assertEqual(namespace["ETL_Date"], "2026-10-21")

    def test_no_ambient_environment_fallback(self):
        self.private["values"].pop("HRM_TOKEN")
        self.save()
        with patch.dict(os.environ, dict(HRM_TOKEN="ambient-must-not-be-used")):
            with self.assertRaisesRegex(ValueError, "HRM_TOKEN"):
                self.build()

    def test_missing_private_file(self):
        (self.root / "config" / "secrets" / "dev.local.json").unlink()
        with self.assertRaisesRegex(ValueError, "dev.local.json"):
            self.build()

    def test_environment_label_mismatch(self):
        self.private["environment"] = "prod"
        self.save()
        with self.assertRaisesRegex(ValueError, "label mismatch"):
            self.build()

    def test_unconfigured_uat_cannot_borrow_dev(self):
        self.profile = json.loads((ROOT / "config" / "environments" / "uat.json").read_text())
        self.private["environment"] = "uat"
        self.save("uat")
        with self.assertRaisesRegex(ValueError, "Missing configured names"):
            job_environment("uat", "landing", "hrm", "unit", root=self.root)

    def test_reject_secrets_in_public_profile(self):
        self.profile["variables"][next(iter(SECRET_NAMES))] = "offline-only"
        self.save()
        with self.assertRaisesRegex(ValueError, "public environment"):
            self.build()

    def test_source_options_cannot_override_environment(self):
        self.profile["source_options"]["hrm"]["PIPELINE_ENV"] = "prod"
        self.save()
        with self.assertRaisesRegex(ValueError, "cannot be overridden"):
            self.build()

    def test_vlp_window_supported_only_on_landing(self):
        values = self.build("landing", "vlp", "order_detail", date_from="2020-01-01", date_to="2026-10-22")
        self.assertEqual(values["VLP_DATE_FROM"], "2020-01-01")
        for layer, source, object_name in (("bronze", "vlp", "order_detail"), ("landing", "hrm", "unit")):
            with self.subTest(layer=layer, source=source):
                with self.assertRaisesRegex(ValueError, "only for VLP Landing"):
                    self.build(layer, source, object_name, date_from="2020-01-01", date_to="2026-10-22")

    def test_invalid_dates_and_incomplete_window(self):
        for batch in ("2026-2-1", "2026-02-30", "invalid"):
            with self.subTest(batch=batch), self.assertRaises(ValueError):
                job_environment("dev", "landing", "hrm", "unit", batch, root=self.root)
        with self.assertRaises(ValueError):
            self.build("landing", "vlp", "order_detail", date_from="2026-10-22", date_to="2026-10-21")
        with self.assertRaises(ValueError):
            self.build("landing", "vlp", "order_detail", date_from="2026-10-21")

    def test_draft_is_not_deployable(self):
        with self.assertRaisesRegex(ValueError, "draft is not a job"):
            job_environment("dev", "gold", "cas_admin", "dim_org", root=self.root)

    def test_newlines_and_placeholders_rejected(self):
        for value in ("invalid\nline", "<provide-local-value>", ""):
            self.private["values"]["HRM_TOKEN"] = value
            self.save()
            with self.subTest(value_kind=type(value).__name__), self.assertRaises(ValueError):
                self.build()

    def test_custom_warehouse_keys_and_catalog(self):
        self.profile["catalogs"]["bronze"] = "bronze_test"
        self.save()
        values = self.build("bronze")
        self.assertEqual(values["ACCESS_KEY1"], self.private["values"]["ACCESS_KEY1"])
        self.assertEqual(values["TABLE_NAME"], "bronze_test.hrm.unit")
        self.assertEqual(values["LOG_TABLE"], "bronze_test.pipeline.log_pipeline")

    def test_private_export_and_path_boundary(self):
        values = self.build()
        destination = write_job_environment(values, self.root / ".local" / "jobs" / "dev.env", self.root)
        self.assertEqual(destination.read_text(), "".join(f"{key}={value}\n" for key, value in sorted(values.items())))
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)
        with self.assertRaisesRegex(ValueError, "only under .local"):
            write_job_environment(values, self.root / "tracked.env", self.root)


class SourceTests(unittest.TestCase):
    def test_source_validation(self):
        errors, summary = validate()
        self.assertEqual(errors, [])
        self.assertEqual(summary["notebooks"], 7)

    def test_private_paths_never_selected_for_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [".local/handoff/context.md", "config/secrets/dev.local.json",
                     "config/secrets/wrong-name.json", "config/secrets/secrets.example.json",
                     "config/secrets/README.md", "README.md", ".env", "dist/old.zip"]
            for relative in paths:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("offline fixture")
            selected = {path.relative_to(root).as_posix() for path in source_files(root)}
            self.assertEqual(selected, {"README.md", "config/secrets/secrets.example.json", "config/secrets/README.md"})

    @unittest.skipUnless(shutil.which("git"), "git not installed")
    def test_git_ignore_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(ROOT / ".gitignore", root / ".gitignore")
            subprocess.run(["git", "init", "--quiet", "--template="], cwd=root, check=True, capture_output=True)
            for relative in ("config/secrets/dev.local.json", "config/secrets/unknown.json", ".local/jobs/test.env"):
                result = subprocess.run(["git", "check-ignore", "--no-index", relative], cwd=root, capture_output=True)
                self.assertEqual(result.returncode, 0, relative)
            for relative in ("config/secrets/secrets.example.json", "config/secrets/README.md", "config/environments/dev.json"):
                result = subprocess.run(["git", "check-ignore", "--no-index", relative], cwd=root, capture_output=True)
                self.assertEqual(result.returncode, 1, relative)

    def test_vlp_synthetic_signature_fixture(self):
        path = ROOT / "notebooks" / "landing" / "vlp" / "NB_landing.vlp.order_detail.ipynb"
        notebook = json.loads(path.read_text())
        names = {"java_value", "flatten_array", "flatten_object", "calculate_sign"}
        namespace = {}
        import hashlib
        namespace.update(hashlib=hashlib, json=json, re=re)
        fixture = None
        for cell in notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            code = "".join(cell["source"])
            nodes = [node for node in ast.parse(code).body if isinstance(node, ast.FunctionDef) and node.name in names]
            if nodes:
                exec(compile(ast.Module(body=nodes, type_ignores=[]), path.name, "exec"), namespace)
            if "assert calculate_sign(sample_body," in code:
                fixture = code
        self.assertIsNotNone(fixture)
        exec(compile(fixture, path.name, "exec"), namespace)


if __name__ == "__main__":
    unittest.main()
