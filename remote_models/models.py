import logging
import urllib
from typing import Any, List, Optional, Type

import requests

from .exceptions import GenericFailedRequest, RemoteModelTimeOutException
from .responses import BasePaginatedResponse, BaseResponse

logger = logging.getLogger("tasks.generic.models")


class RemoteModel:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def _header(self):
        return {
            "content-type": "application/json",
        }

    def _url(self, entity: str, **params) -> str:
        """Converts params to query string and returns url

        Returns:
            str: URL with query string
        """
        encoded_params = urllib.parse.urlencode(params) if params else ""

        return f"{self.base_url}{entity}/?{encoded_params}"

    def raise_for_status(self, response: requests.Response, url: Optional[str]) -> None:
        """Raises exception if status code is not 200

        Args:
            response (requests.Response): Response object
            url (Optional[str]): Request URL

        Raises:
            GenericFailedRequest: Exception raised
        """
        if response.status_code >= 400:
            raise GenericFailedRequest(f"Response: {response.text} URL: {url}")

    def filter(
        self, entity: str, response_class: Type[BasePaginatedResponse], **conditions
    ) -> BasePaginatedResponse:
        """Request to remote model with filters, returns paginated result

        Returns:
            _type_: REST API Response
        """

        url = self._url(entity, **conditions)

        try:
            response: requests.Response = requests.get(
                url, headers=self._header(), timeout=10
            )
        except requests.exceptions.Timeout as exc:
            logger.exception(f"[!!!] Time out exception: {exc}")
            raise RemoteModelTimeOutException(exc)

        self.raise_for_status(response, url)

        return response_class(**response.json())

    def filter_all(
        self, entity: str, response_class: Type[BasePaginatedResponse], **conditions
    ) -> BasePaginatedResponse:
        """Filter all remote records

        Args:
            response_class (Type[BaseResponse]): Type of the response class

        Raises:
            RemoteModelTimeOutException: Time Out exception raised

        Returns:
            Type[BaseResponse]: Return response object
        """

        response = self.filter(entity, response_class, **conditions)

        results: List[Any] = response.results

        while response.next:
            try:
                r: requests.Response = requests.get(
                    response.next, headers=self._header(), timeout=10
                )
            except requests.exceptions.Timeout as exc:
                logger.exception(f"[!!!] Time out exception: {exc}")
                raise RemoteModelTimeOutException(exc)

            response = response_class(**r.json())
            results.extend(response.results)

        return response_class(count=len(results), results=results)

    def save(
        self, entity: str, response_class: Type[BaseResponse], **fields_values
    ) -> BaseResponse:
        """Request to remote model with filters, returns paginated result

        Returns:
            _type_: REST API Response
        """

        url = self._url(entity)

        try:
            response: requests.Response = requests.post(
                url, json=fields_values, headers=self._header(), timeout=10
            )
        except requests.exceptions.Timeout as exc:
            logger.exception(f"[!!!] Time out exception: {exc}")
            raise RemoteModelTimeOutException(exc)

        self.raise_for_status(response, url)

        return response_class(**response.json())
