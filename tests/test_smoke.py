"""Smoke tests — no live poe.ninja calls (static routes + settings JSON only)."""
from __future__ import annotations

import unittest


class TestAppSmoke(unittest.TestCase):
    """Minimal Flask app health checks."""

    @classmethod
    def setUpClass(cls) -> None:
        import app as app_module

        cls.client = app_module.app.test_client()

    def test_index_returns_200(self) -> None:
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"POE", r.data)

    def test_api_settings_returns_200(self) -> None:
        r = self.client.get("/api/settings")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("settings", data)

    def test_api_settings_includes_fetch_flag_types(self) -> None:
        r = self.client.get("/api/settings")
        by_key = {s["key"]: s for s in r.get_json()["settings"]}
        self.assertEqual(by_key["FETCH_CRAFTING_FULL_SWEEP"]["type"], "bool")
        self.assertEqual(by_key["FETCH_POE1_ESSENCE_EXCHANGE"]["type"], "bool")
        self.assertEqual(by_key["FETCH_POE1_TATTOO_OVERVIEW"]["type"], "bool")


if __name__ == "__main__":
    unittest.main()
