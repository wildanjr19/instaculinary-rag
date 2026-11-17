import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.embedding import JinaEmbedding
from src.llm import load_llm


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        config_dir = self.root / "config"
        config_dir.mkdir()
        self.config_path = config_dir / "config.py"
        source = Path(__file__).resolve().parents[1] / "config" / "config.py"
        shutil.copyfile(source, self.config_path)
        (self.root / ".env").write_text(
            "PINECONE_INDEX_NAME=file-index\nJINA_AI_API_KEY=file-key\n",
            encoding="utf-8",
        )

    def load_config(self):
        spec = importlib.util.spec_from_file_location("isolated_config", self.config_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_loads_dotenv_and_data_path_from_project_root(self):
        # Konfigurasi disalin ke root sementara; cwd tetap di luar root tersebut.
        with patch.dict(os.environ, {}, clear=True):
            config = self.load_config()
            self.assertEqual(config.PINECONE_INDEX_NAME, "file-index")
            self.assertEqual(config.get_required_env("JINA_AI_API_KEY"), "file-key")
            self.assertEqual(config.DATA_DIR, self.root / "data/04_knowledge_base/knowledge_base_v2.csv")

    def test_shell_environment_takes_priority(self):
        with patch.dict(os.environ, {"PINECONE_INDEX_NAME": "shell-index"}, clear=True):
            config = self.load_config()
            self.assertEqual(config.PINECONE_INDEX_NAME, "shell-index")

    def test_missing_or_blank_credentials_are_reported_by_name(self):
        with patch.dict(os.environ, {}, clear=True):
            config = self.load_config()
            for value in (None, "", "   "):
                with self.subTest(value=value):
                    if value is not None:
                        os.environ["DEEPSEEK_API_KEY"] = value
                    with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
                        config.get_required_env("DEEPSEEK_API_KEY")

    def test_api_clients_fail_before_network_when_keys_are_missing(self):
        load_llm.cache_clear()
        self.addCleanup(load_llm.cache_clear)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
                load_llm()
            with self.assertRaisesRegex(ValueError, "JINA_AI_API_KEY"):
                JinaEmbedding()

    def test_installed_app_starts_outside_repository_without_credentials(self):
        env = os.environ.copy()
        for name in ("DEEPSEEK_API_KEY", "JINA_AI_API_KEY", "PINECONE_API_KEY", "PYTHONPATH"):
            env.pop(name, None)
        env["PYTHON_DOTENV_DISABLED"] = "1"
        result = subprocess.run(
            [sys.executable, "-c", (
                "from backend.api import app; "
                "from src import main, create_vector_db; "
                "from fastapi.testclient import TestClient; "
                "client = TestClient(app); "
                "assert client.get('/').status_code == 200; "
                "client.close(); print('ok')"
            )],
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ok")
