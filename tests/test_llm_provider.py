"""Tests for the LLM provider component, using mocked subprocess calls."""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

import pathsetup  # noqa: F401

from nexus.components import llm_provider


class TestLLMProvider(unittest.TestCase):

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_is_ollama_installed_true(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(llm_provider.is_ollama_installed())

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_is_ollama_installed_false_when_missing(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        self.assertFalse(llm_provider.is_ollama_installed())

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_is_ollama_installed_false_on_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "ollama")
        self.assertFalse(llm_provider.is_ollama_installed())

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_list_models(self, mock_run):
        mock_run.return_value = MagicMock(stdout="ministral-3\tlatest\n")
        self.assertIn("ministral-3", llm_provider.list_models())

    @patch("nexus.components.llm_provider.list_models")
    def test_is_model_available_true(self, mock_list):
        mock_list.return_value = "ministral-3\tlatest\n"
        self.assertTrue(llm_provider.is_model_available("ministral-3"))

    @patch("nexus.components.llm_provider.list_models")
    def test_is_model_available_false(self, mock_list):
        mock_list.return_value = "llama3\tlatest\n"
        self.assertFalse(llm_provider.is_model_available("ministral-3"))

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_ask_returns_stripped_stdout(self, mock_run):
        mock_run.return_value = MagicMock(stdout="  Hello there  \n")
        result = llm_provider.ask("hi")
        self.assertEqual(result, "Hello there")

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_ask_handles_called_process_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "ollama", stderr="model not found"
        )
        result = llm_provider.ask("hi")
        self.assertIn("Error calling Ollama", result)

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_ask_handles_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("ollama", 120)
        result = llm_provider.ask("hi")
        self.assertIn("timed out", result)

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_ask_handles_missing_binary(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        result = llm_provider.ask("hi")
        self.assertIn("not installed", result)

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_pull_model_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(llm_provider.pull_model("ministral-3"))

    @patch("nexus.components.llm_provider.subprocess.run")
    def test_pull_model_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "ollama")
        self.assertFalse(llm_provider.pull_model("ministral-3"))


if __name__ == "__main__":
    unittest.main()
