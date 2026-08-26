"""Unit tests for the qsm-medi Flywheel gear entry point."""

import json
import sys
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src/flywheel to path so we can import the run module
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "flywheel"))

# Mock flywheel before importing run (run.py imports flywheel at module level)
sys.modules["flywheel"] = MagicMock()

import run  # noqa: E402


class TestSafeExtractZip:
    """Tests for zip-slip protection in safe_extract_zip."""

    def test_extracts_valid_zip(self, tmp_path):
        """A zip with normal entries extracts successfully."""
        zip_path = tmp_path / "good.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file.txt", "hello")
            zf.writestr("subdir/nested.txt", "world")

        dest = tmp_path / "output"
        dest.mkdir()

        run.safe_extract_zip(str(zip_path), str(dest))

        assert (dest / "file.txt").read_text() == "hello"
        assert (dest / "subdir" / "nested.txt").read_text() == "world"

    def test_rejects_path_traversal(self, tmp_path):
        """A zip entry with ../ path traversal raises ValueError."""
        zip_path = tmp_path / "evil.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("../escaped.txt", "malicious")

        dest = tmp_path / "output"
        dest.mkdir()

        with pytest.raises(ValueError, match="escape target directory"):
            run.safe_extract_zip(str(zip_path), str(dest))

    def test_rejects_absolute_path_entry(self, tmp_path):
        """A zip entry with an absolute path raises ValueError."""
        zip_path = tmp_path / "abs.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("/etc/passwd", "nope")

        dest = tmp_path / "output"
        dest.mkdir()

        with pytest.raises(ValueError, match="escape target directory"):
            run.safe_extract_zip(str(zip_path), str(dest))

    def test_empty_zip(self, tmp_path):
        """An empty zip extracts without error."""
        zip_path = tmp_path / "empty.zip"
        with zipfile.ZipFile(zip_path, "w"):
            pass

        dest = tmp_path / "output"
        dest.mkdir()

        run.safe_extract_zip(str(zip_path), str(dest))
        assert list(dest.iterdir()) == []


class TestCreateParametersJson:
    """Tests for config-to-JSON serialization."""

    def _make_mock_context(self, config_dict):
        """Create a mock GearContext with the given config values."""
        ctx = MagicMock()
        ctx.config.get = lambda key, default=None: config_dict.get(key, default)
        return ctx

    def test_writes_only_non_none_values(self, tmp_path, monkeypatch):
        """Only config values that are not None appear in the output JSON."""
        output_json = tmp_path / "parameters" / "qsm_parameters.json"
        monkeypatch.setattr(run, "PATH_PARAMETERS_JSON", output_json)

        context = self._make_mock_context({
            "medi_lambda": 1000,
            "pdf_tol": 0.1,
            "debug_mode": 1,
        })

        run.create_parameters_json(context)

        result = json.loads(output_json.read_text())
        assert result == {
            "medi_lambda": 1000,
            "pdf_tol": 0.1,
            "debug_mode": 1,
        }

    def test_writes_empty_dict_when_all_none(self, tmp_path, monkeypatch):
        """When no config values are set, writes an empty JSON object."""
        output_json = tmp_path / "parameters" / "qsm_parameters.json"
        monkeypatch.setattr(run, "PATH_PARAMETERS_JSON", output_json)

        context = self._make_mock_context({})

        run.create_parameters_json(context)

        result = json.loads(output_json.read_text())
        assert result == {}

    def test_creates_parent_directories(self, tmp_path, monkeypatch):
        """Parent directories are created if they don't exist."""
        output_json = tmp_path / "deep" / "nested" / "params.json"
        monkeypatch.setattr(run, "PATH_PARAMETERS_JSON", output_json)

        context = self._make_mock_context({})

        run.create_parameters_json(context)
        assert output_json.exists()


class TestConfigVariablesMatchManifest:
    """Verify CONFIG_VARIABLES stays in sync with the manifest."""

    @pytest.fixture()
    def manifest_config_keys(self):
        """Load config keys from manifest.json."""
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)
        return set(manifest["config"].keys())

    def test_all_manifest_configs_are_in_config_variables(
        self, manifest_config_keys
    ):
        """Every manifest config key should appear in CONFIG_VARIABLES.

        This catches the bug where a manifest config key is spelled
        differently in the Python code (e.g., tol_norm_ratio vs
        medi_tol_norm_ratio).
        """
        code_vars = set(run.CONFIG_VARIABLES)
        missing = manifest_config_keys - code_vars
        assert missing == set(), (
            f"Manifest config keys not in CONFIG_VARIABLES: {missing}"
        )

    def test_all_config_variables_are_in_manifest(self, manifest_config_keys):
        """Every CONFIG_VARIABLES entry should exist in the manifest.

        This catches stale entries that were removed from the manifest
        but left in the code.
        """
        code_vars = set(run.CONFIG_VARIABLES)
        extra = code_vars - manifest_config_keys
        assert extra == set(), (
            f"CONFIG_VARIABLES entries not in manifest: {extra}"
        )
