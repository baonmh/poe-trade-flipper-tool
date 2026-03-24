"""Smoke tests — no live poe.ninja / GGG calls (mocked routes + offline league fallback)."""
from __future__ import annotations

import unittest
from unittest.mock import patch


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
        self.assertEqual(by_key["EXCHANGE_USE_OVERVIEW_ONLY"]["type"], "bool")

    @patch("app.ninja.get_currency_rates", return_value=[])
    def test_api_rates_returns_json_shape(self, _mock_rates) -> None:
        r = self.client.get("/api/rates")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("meta", data)
        self.assertIn("rates", data)
        self.assertIn("all_rates", data)
        self.assertIsInstance(data["rates"], list)
        self.assertIsInstance(data["all_rates"], list)
        self.assertIn("exchange_overview_only", data["meta"])

    @patch("app.ninja.get_currency_rates", return_value=[])
    def test_api_flips_returns_json_shape(self, _mock_rates) -> None:
        r = self.client.get("/api/flips")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("meta", data)
        self.assertIn("direct", data)
        self.assertIsInstance(data["direct"], list)

    @patch("app.ninja.get_all_crafting_items", return_value=[])
    @patch("app.ninja.get_currency_rates", return_value=[])
    def test_api_crafting_returns_json_shape(self, _mock_rates, _mock_items) -> None:
        r = self.client.get("/api/crafting")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("meta", data)
        self.assertIn("hotspots", data)
        self.assertIn("bulk", data)
        self.assertIsInstance(data["hotspots"], list)
        self.assertIsInstance(data["bulk"], list)

    @patch("app.ninja.get_currency_rates", return_value=[])
    def test_api_convert_tricks_returns_json_shape(self, _mock_rates) -> None:
        r = self.client.get("/api/convert-tricks")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("meta", data)
        self.assertIn("computed", data)
        self.assertIn("research", data)
        self.assertIsInstance(data["computed"], list)
        self.assertIsInstance(data["research"], list)

    @patch("app.ninja.get_currency_rates", return_value=[])
    def test_api_trade_suggestions_returns_json_shape(self, _mock_rates) -> None:
        r = self.client.get("/api/trade-suggestions")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("meta", data)
        self.assertIn("direct", data)
        self.assertIsInstance(data["direct"], list)

    def test_api_trade_pair_diff_empty_sections(self) -> None:
        r = self.client.post(
            "/api/trade-pair-diff",
            json={"sections": []},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, dict)

    def test_api_clear_cache_post(self) -> None:
        r = self.client.post("/api/clear-cache")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), {"ok": True})

    @patch("app.ninja.store_currency_rates_cache")
    @patch("app.ninja.iter_currency_rates_batches")
    def test_api_economy_stream_returns_sse_with_rates_and_flips(self, mock_batches, _mock_store) -> None:
        """Single iterator feeds both Rates + Flips payloads (no duplicate economy fetch)."""
        mock_batches.return_value = iter([(1, 1, "Currency", [])])
        r = self.client.get("/api/economy/stream")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/event-stream", r.headers.get("Content-Type", ""))
        body = r.get_data(as_text=True)
        self.assertIn("stream_done", body)
        self.assertIn('"rates"', body)
        self.assertIn("all_rates", body)
        self.assertIn('"flips"', body)
        self.assertIn("direct", body)

    @patch("app.ninja.iter_crafting_item_batches")
    @patch("app.ninja.get_currency_rates", return_value=[])
    def test_api_crafting_stream_returns_sse_with_done(self, _mock_rates, mock_craft_batches) -> None:
        mock_craft_batches.return_value = iter([(1, 1, "TestCat", [])])
        r = self.client.get("/api/crafting/stream")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/event-stream", r.headers.get("Content-Type", ""))
        body = r.get_data(as_text=True)
        self.assertIn("stream_done", body)
        self.assertIn("hotspots", body)

    @patch("app.requests.get", side_effect=Exception("offline"))
    def test_api_leagues_fallback_when_ggg_unreachable(self, _mock_get) -> None:
        r = self.client.get("/api/leagues?game=poe2")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("leagues", data)
        self.assertIsInstance(data["leagues"], list)
        self.assertGreaterEqual(len(data["leagues"]), 1)


if __name__ == "__main__":
    unittest.main()
