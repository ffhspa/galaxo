import json
import time
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from playwright.async_api import async_playwright
from CONFIG.Constants import Constants


class PlaywrightService:
    """Singleton service that runs one asyncio event loop in a background thread
    and owns a single Playwright browser/context/page to be reused for requests.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # background loop + thread
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        # attributes populated by _start_async
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

        # start Playwright inside the background loop and wait for completion
        fut = asyncio.run_coroutine_threadsafe(self._start_async(), self.loop)
        fut.result()  # wait until ready

    def _run_loop(self):
        # Bind the loop to this thread and run forever
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _start_async(self):
        self._playwright = await async_playwright().start()
        # you can change browser to chromium or webkit if you prefer
        self._browser = await self._playwright.firefox.launch(headless=True)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        # optional: set default timeout for the page requests
        # self._page.set_default_timeout(30_000)

    def submit_coro(self,coro):
        """Schedule a coroutine in the background loop and return a concurrent.futures.Future."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    @classmethod
    def instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = PlaywrightService()
            return cls._instance

    def close(self):
        """Shut down Playwright and stop the loop. Call explicitly when your program exits."""
        if self._playwright is None:
            return
        fut = self.submit_coro(self._close_async())
        fut.result()
        # stop loop and join thread
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()

    async def _close_async(self):
        try:
            if self._page is not None:
                await self._page.close()
            if self._context is not None:
                await self._context.close()
            if self._browser is not None:
                await self._browser.close()
            if self._playwright is not None:
                await self._playwright.stop()
        except Exception:
            # ignore errors on shutdown
            pass


class RequestGraphQLClient:
    """GraphQL client that uses the shared PlaywrightService.
    send_request(...) is synchronous from caller perspective, but runs the actual work
    inside the service's background loop so many requests can run concurrently.
    """

    BASE_URL = Constants.BASE_URL

    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0, timeout: int = 5) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        # keep timeout in milliseconds for Playwright
        self.timeout_ms = timeout * 1000
        self._service = PlaywrightService.instance()

    async def _request_coro(self, payload: Any):
        """Coroutine executed inside the background loop. Implements retries/backoff async."""
        page = self._service._page
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = await page.request.post(
                    self.BASE_URL,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json", **Constants.HEADERS},
                    timeout=self.timeout_ms,
                )

                if not resp.ok:
                    raise Exception(f"HTTP {resp.status}")

                data = await resp.json()

                if "errors" in data:
                    Constants.LOGGER.error(f"GraphQL errors: {data['errors']}")
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
                Constants.LOGGER.info(f"[RequestGraphQLClient] Retrying in {sleep_time:.1f} seconds...")
                await asyncio.sleep(sleep_time)

    def send_request(self, payload: Any, future_timeout: float = None):
        """Sync method for callers: schedules the async coroutine and waits for result.
        future_timeout is an optional timeout (seconds) to wait for whole operation.
        """
        fut = self._service.submit_coro(self._request_coro(payload))
        # block until finished (safe because coroutine runs in the background loop thread)
        try:
            return fut.result(timeout=future_timeout)
        except Exception as e:
            # bubble up (or wrap) the exception as before
            raise

    def close(self):
        # optional: nothing to do per-client because service is shared
        pass
