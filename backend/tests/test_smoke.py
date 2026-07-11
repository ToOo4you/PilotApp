import unittest
from urllib.request import urlopen

BASE_URL = "http://127.0.0.1:8000"


def get_status_code(path: str) -> int:
    with urlopen(f"{BASE_URL}{path}", timeout=3) as response:
        return response.getcode()


def get_headers(path: str):
    with urlopen(f"{BASE_URL}{path}", timeout=3) as response:
        return {k.lower(): v for k, v in response.headers.items()}


class SmokeTests(unittest.TestCase):
    def test_root_returns_ok(self) -> None:
        self.assertEqual(get_status_code("/"), 200)

    def test_metrics_returns_ok(self) -> None:
        self.assertEqual(get_status_code("/metrics"), 200)

    def test_root_rate_limit_headers_present(self) -> None:
        headers = get_headers("/")
        self.assertIn("x-ratelimit-limit", headers)
        self.assertIn("x-ratelimit-remaining", headers)


    def test_customers_returns_list(self) -> None:
        self.assertEqual(get_status_code("/customers/"), 200)


    def test_companies_returns_list(self) -> None:
        self.assertEqual(get_status_code("/companies/"), 200)


    def test_ai_health_returns_healthy(self) -> None:
        self.assertEqual(get_status_code("/api/ai/health"), 200)

    def test_operations_dot_regulations_returns_ok(self) -> None:
        self.assertEqual(get_status_code("/ops/dot-regulations"), 200)

    def test_operations_hos_summary_returns_ok(self) -> None:
        self.assertEqual(get_status_code("/ops/logbooks/D-1001/hos-summary"), 200)


if __name__ == "__main__":
    unittest.main()
