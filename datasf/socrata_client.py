import os
from requests import (
    Session,
    HTTPError,
)

from typing import (
    Any,
)
import logging

LOGGER = logging.getLogger(__name__)


class SocrataClient(object):
    URI_SCHEME = "https:"
    API_PATH = "resource"
    # If we need to handle other types of content functionality can be added to generalize the client
    CONTENT_TYPE = "json"
    _instance = None

    def __init__(self, server, dataset_id, username=None, password=None, api_key=None):
        """
        Allows credentials to be set as environment variables to avoid printing them out or storing in cod
        :param server: host to connect to
        :param dataset_id: id of the dataset to query
        :param username: user to authenticate as
        :param password: password to authenticate with
        :param api_key: user's api key, can be used in place of the user/pass pair, when provided takes precedence
        """
        self.host = server
        self.dataset_id = dataset_id
        self.session = Session()

        # checks if api_key is provided as param or in environment
        token = api_key or os.getenv("API_KEY", None)
        if token:
            # sets auth header
            self.session.headers["Authorization"] = f"Basic {token}"
        else:
            # checks if username and password are provided in env or as params
            username = username or os.getenv("USERNAME", None)
            password = password or os.getenv("PASSWORD", None)
            if username and password:
                # sets auth header using requests facilities
                self.session.auth = (username, password)

    def __enter__(self):
        """
        Implements an entry part of the with block for an auto-closable class
        :return: object
        """
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        """
        Implements an exit part of the with block for an auto-closable class
        Closes the requests session0
        :return:
        """
        self.session.close()

    def get_request_uri(self) -> str:
        return f"{self.URI_SCHEME}//{self.host}/{self.API_PATH}/{self.dataset_id}.{self.CONTENT_TYPE}"

    def _process_response(self, response) -> Any:
        """
        Internal method to handle response from server
        :return: json payload as dict
        :raises: HttpError
        """
        if response.status_code not in (200, 202, 409):
            raise HTTPError(f"Request returned code: {response.status_code}, message: {response.text}")
        if response.status_code == 409:
            LOGGER.error("You're being rate limited please use credentials")
            return None
        return response.json()

    def get(self, query: str, timeout: int = 30):
        """
        Returns results of the query on the specified dataset
        :param query: raw SoQL query
        :param timeout: request timeout in seconds
        :return: List of results
        """
        self.session.headers["Accept"] = self.CONTENT_TYPE
        uri = self.get_request_uri()
        LOGGER.debug("Dataset URI: %s", uri)
        resp = self.session.get(url=uri, params={"$query": query}, timeout=timeout)
        return self._process_response(response=resp)
