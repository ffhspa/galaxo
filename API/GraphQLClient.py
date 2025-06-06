import json
import time
import asyncio
from playwright.async_api import async_playwright
from CONFIG.Constants import Constants

class GraphQLClient:
    """GraphQL client using Playwright. Instances share a single browser."""

    BASE_URL = Constants.BASE_URL

    _loop = None
    _playwright = None
    _browser = None
    _context = None
    _page = None
    _instances = 0

    def __init__(self, max_retries: int = 5, backoff_factor: float = 1.0, timeout: int = 5) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

        GraphQLClient._instances += 1
        if GraphQLClient._loop is None:
            GraphQLClient._loop = asyncio.new_event_loop()
            GraphQLClient._playwright = GraphQLClient._loop.run_until_complete(async_playwright().start())
            GraphQLClient._browser = GraphQLClient._loop.run_until_complete(
                GraphQLClient._playwright.firefox.launch(headless=True)
            )
            GraphQLClient._context = GraphQLClient._loop.run_until_complete(GraphQLClient._browser.new_context())
            GraphQLClient._page = GraphQLClient._loop.run_until_complete(GraphQLClient._context.new_page())

    def send_request(self, payload):
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = GraphQLClient._loop.run_until_complete(
                    GraphQLClient._page.request.post(
                        self.BASE_URL,
                        data=json.dumps(payload),
                        headers={"Content-Type": "application/json", **Constants.HEADERS},
                        timeout=self.timeout * 1000,
                    )
                )

                if not resp.ok:
                    raise Exception(f"HTTP {resp.status}")

                response_content = GraphQLClient._loop.run_until_complete(resp.json())

                if "errors" in response_content:
                    Constants.LOGGER.error(f"GraphQL errors: {response_content['errors']}")
                    raise Exception(f"GraphQL errors: {response_content['errors']}")

                return response_content

            except Exception as e:
                Constants.LOGGER.warning(
                    f"[GraphQLClient] Payload: {payload} :Attempt {attempt} failed: {e}"
                )

                if attempt == self.max_retries:
                    Constants.LOGGER.error(
                        f"[GraphQLClient] Max retries {self.max_retries} reached. Giving up."
                    )
                    raise

                sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                Constants.LOGGER.info(f"[GraphQLClient] Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)

    def close(self) -> None:
        if GraphQLClient._instances > 0:
            GraphQLClient._instances -= 1

        if GraphQLClient._instances == 0 and GraphQLClient._loop and not GraphQLClient._loop.is_closed():
            if GraphQLClient._page is not None:
                GraphQLClient._loop.run_until_complete(GraphQLClient._page.close())
                GraphQLClient._page = None
            if GraphQLClient._context is not None:
                GraphQLClient._loop.run_until_complete(GraphQLClient._context.close())
                GraphQLClient._context = None
            if GraphQLClient._browser is not None:
                GraphQLClient._loop.run_until_complete(GraphQLClient._browser.close())
                GraphQLClient._browser = None
            if GraphQLClient._playwright is not None:
                GraphQLClient._loop.run_until_complete(GraphQLClient._playwright.stop())
                GraphQLClient._playwright = None
            GraphQLClient._loop.close()
            GraphQLClient._loop = None

    def __del__(self) -> None:
        self.close()
