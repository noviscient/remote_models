import logging
import urllib
from typing import Any, List, Optional, Type

import requests

from .exceptions import GenericFailedRequest, RemoteModelTimeOutException
from .responses import BasePaginatedResponse, BaseResponse

logger = logging.getLogger("tasks.generic.models")


class RemoteModel:
    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self.base_url = base_url
        self.timeout = timeout

        self.session = requests.Session()
        self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
        self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

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
            BaseResponse: REST API Response
        """

        url = self._url(entity, **conditions)

        try:
            with self.session.get(
                url, headers=self._header(), timeout=self.timeout
            ) as response:

                self.raise_for_status(response, url)
                response_data = response_class(
                    **response.json(), http_response=response
                )

        except requests.exceptions.Timeout as exc:
            logger.exception(f"[!!!] Time out exception: {exc}")
            raise RemoteModelTimeOutException(exc)

        else:
            return response_data

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

        response_data = self.filter(entity, response_class, **conditions)

        results: List[Any] = response_data.results

        while response_data.next:
            try:
                with self.session.get(
                    response_data.next, headers=self._header(), timeout=self.timeout
                ) as response:

                    self.raise_for_status(response, response_data.next)
                    response_data = response_class(
                        **response.json(), http_response=response
                    )

            except requests.exceptions.Timeout as exc:
                logger.exception(f"[!!!] Time out exception: {exc}")
                raise RemoteModelTimeOutException(exc)

            else:
                results.extend(response_data.results)

        return response_class(count=len(results), results=results)

    def create(
        self, entity: str, response_class: Type[BaseResponse], **fields_values
    ) -> BaseResponse:
        """POST request to remote model

        Returns:
            _type_: REST API Response
        """

        url = self._url(entity)

        try:
            with self.session.post(
                url, json=fields_values, headers=self._header(), timeout=self.timeout
            ) as response:

                self.raise_for_status(response, url)
                response_data = response_class(
                    **response.json(), http_response=response
                )

        except requests.exceptions.Timeout as exc:
            logger.exception(f"[!!!] Time out exception: {exc}")
            raise RemoteModelTimeOutException(exc)

        else:
            return response_data

    def create_bulk(
        self, entity: str, response_class: Type[BaseResponse], bulk_data: list
    ) -> BaseResponse:
        """POST request to remote model

        Returns:
            _type_: REST API Response
        """

        url = self._url(entity)

        try:
            with self.session.post(
                url, json=bulk_data, headers=self._header(), timeout=self.timeout
            ) as response:

                self.raise_for_status(response, url)
                response_data = response_class(http_response=response)

        except requests.exceptions.Timeout as exc:
            logger.exception(f"[!!!] Time out exception: {exc}")
            raise RemoteModelTimeOutException(exc)

        else:
            return response_data

    def update(
        self, entity: str, response_class: Type[BaseResponse], **fields_values
    ) -> BaseResponse:
        """PATCH request to remote model

        Returns:
            _type_: REST API Response
        """

        url = self._url(entity)

        try:
            with self.session.patch(
                url, json=fields_values, headers=self._header(), timeout=self.timeout
            ) as response:

                self.raise_for_status(response, url)
                response_data = response_class(
                    **response.json(), http_response=response
                )

        except requests.exceptions.Timeout as exc:
            logger.exception(f"[!!!] Time out exception: {exc}")
            raise RemoteModelTimeOutException(exc)

        else:
            return response_data

    def delete(
        self, entity: str, response_class: Type[BaseResponse], **fields_values
    ) -> BaseResponse:
        """DELETE request to remote model

        Returns:
            _type_: REST API Response
        """

        url = self._url(entity)

        try:
            response = self.session.delete(
                url, json=fields_values, headers=self._header(), timeout=self.timeout
            )

            self.raise_for_status(response, url)

            if response.status_code == 204 and len(response.content) == 0:
                response_data = response_class(http_response=response)
            else:
                response_data = response_class(
                    **response.json(), http_response=response
                )

        except requests.exceptions.Timeout as exc:
            raise RemoteModelTimeOutException(exc)
        else:
            return response_data
