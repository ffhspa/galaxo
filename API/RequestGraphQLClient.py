import json
import time
import requests
from requests.adapters import HTTPAdapter
from CONFIG.Constants import Constants

class RequestGraphQLClient:
    """Lightweight GraphQL client using the requests library."""

    BASE_URL = Constants.BASE_URL

    def __init__(self, max_retries: int = 5, backoff_factor: float = 1.0, timeout: int = 5) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self._session = requests.Session()
        adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def send_request(self, payload):
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._session.post(
                    self.BASE_URL,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json", **Constants.HEADERS},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                if "errors" in data:
                    raise Exception(f"GraphQL errors: {data['errors']}")
                return data
            except Exception as e:
                Constants.LOGGER.warning(
                    f"[RequestGraphQLClient] Payload: {payload} :Attempt {attempt} failed: {e}"
                )
                if attempt == self.max_retries:
                    Constants.LOGGER.error(
                        f"[RequestGraphQLClient] Max retries {self.max_retries} reached. Giving up."
                    )
                    raise
                sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                Constants.LOGGER.info(
                    f"[RequestGraphQLClient] Retrying in {sleep_time:.1f} seconds..."
                )
                time.sleep(sleep_time)

    def close(self) -> None:
        self._session.close()

    def __del__(self) -> None:
        self.close()
