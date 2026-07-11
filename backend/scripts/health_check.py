import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Iterable


DEFAULT_ENDPOINTS = (
    "/",
    "/customers/",
    "/companies/",
    "/api/ai/health",
)


def check_endpoints(base_url: str, endpoints: Iterable[str], timeout: float) -> int:
    failures = 0

    for endpoint in endpoints:
        url = f"{base_url.rstrip('/')}{endpoint}"
        try:
            request = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status_code = response.getcode()
                # Read body to ensure the endpoint returns parseable payload when present.
                payload = response.read()
                if payload:
                    try:
                        json.loads(payload.decode("utf-8"))
                    except json.JSONDecodeError:
                        pass

            if status_code >= 400:
                failures += 1
                print(f"FAIL {status_code} {url}")
                continue

            print(f"OK   {status_code} {url}")
        except urllib.error.URLError as exc:
            failures += 1
            print(f"FAIL exception {url}: {exc}")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Backend health check")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base API URL")
    parser.add_argument("--timeout", type=float, default=3.0, help="Request timeout in seconds")
    parser.add_argument(
        "--endpoints",
        nargs="*",
        default=list(DEFAULT_ENDPOINTS),
        help="Endpoints to verify",
    )
    args = parser.parse_args()

    failures = check_endpoints(args.base_url, args.endpoints, args.timeout)
    if failures:
        print(f"Health check failed: {failures} endpoint(s) unhealthy")
        return 1

    print("Health check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
