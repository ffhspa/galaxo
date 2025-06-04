import json
import time
from playwright.sync_api import sync_playwright
from GALAXO.CONFIG.Constants import Constants

class GraphQLClient:
    BASE_URL = Constants.BASE_URL

    def __init__(self, max_retries: int = 5, backoff_factor: float = 1.0, timeout: int = 5) -> None:
        self._playwright = None
        self._context = None
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

    def _ensure_context(self):
        if self._context is None:
            self._playwright = sync_playwright().start()
            self._context = self._playwright.request.new_context(
                extra_http_headers=Constants.HEADERS,
            )
        return self._context

    def send_request(self, payload):
        for attempt in range(1, self.max_retries + 1):
            try:
                ctx = self._ensure_context()
                response = ctx.post(
                    self.BASE_URL,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout * 1000,
                )
                if not response.ok:
                    raise Exception(f"HTTP {response.status}")
                response_content = response.json()

                if "errors" in response_content:
                    Constants.LOGGER.error(f"GraphQL errors: {response_content['errors']}")
                    raise Exception(f"GraphQL errors: {response_content['errors']}")

                return response_content

            except Exception as e:
                Constants.LOGGER.warning(f"[GraphQLClient] Payload: {payload} : Attempt {attempt} failed: {e}")

                if attempt == self.max_retries:
                    Constants.LOGGER.error(f"[GraphQLClient] Max retries {self.max_retries} reached. Giving up.")
                    raise

                sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                Constants.LOGGER.info(f"[GraphQLClient] Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)

    def __del__(self):
        self.close()

    def close(self) -> None:
        if self._context:
            self._context.dispose()
            self._context = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
