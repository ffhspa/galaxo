import json
import time
import asyncio
from playwright.async_api import async_playwright
from GALAXO.CONFIG.Constants import Constants

class GraphQLClient:
    BASE_URL = Constants.BASE_URL

    def __init__(self, max_retries: int = 5, backoff_factor: float = 1.0, timeout: int = 5) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self._loop = asyncio.new_event_loop()
        self._playwright = self._loop.run_until_complete(async_playwright().start())
        self._browser = self._loop.run_until_complete(self._playwright.firefox.launch(headless=True))
        self._context = self._loop.run_until_complete(self._browser.new_context())
        self._page = self._loop.run_until_complete(self._context.new_page())

    def send_request(self, payload):
        return self._loop.run_until_complete(self._send_request(payload))

    async def _send_request(self, payload):
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = await self._page.request.post(
                    self.BASE_URL,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json", **Constants.HEADERS},
                    timeout=self.timeout * 1000,
                )
                if not resp.ok:
                    raise Exception(f"HTTP {resp.status}")
                response_content = await resp.json()

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
                await asyncio.sleep(sleep_time)

    def __del__(self):
        self.close()

    def close(self) -> None:
        if not hasattr(self, "_loop") or self._loop.is_closed():
            return
        if hasattr(self, "_page"):
            self._loop.run_until_complete(self._page.close())
        if hasattr(self, "_context"):
            self._loop.run_until_complete(self._context.close())
        if hasattr(self, "_browser"):
            self._loop.run_until_complete(self._browser.close())
        if hasattr(self, "_playwright"):
            self._loop.run_until_complete(self._playwright.stop())
        self._loop.close()
