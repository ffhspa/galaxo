import requests
import time
from GALAXO.CONFIG.Constants import Constants
from requests.adapters import HTTPAdapter

class GraphQLClient:
    BASE_URL = Constants.BASE_URL

    def __init__(self, max_retries=5, backoff_factor=1.0, timeout=5):
        self._session = None
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(Constants.HEADERS)
            
                    # Hier den Pool vergrößern
            adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
            self._session.mount('http://', adapter)
            self._session.mount('https://', adapter)
            
        return self._session

    def send_request(self, payload):
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    self.BASE_URL,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
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
