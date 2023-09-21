import json
from typing import Any, Dict, List

import pytest
from requests import codes

from remote_models.exceptions import GenericFailedRequest
from remote_models.models import RemoteModel
from remote_models.responses import BasePaginatedResponse, BaseResponse


class RemoteBenchmarkStatesResponse(BasePaginatedResponse):
    results: List[Dict[str, Any]]


class RemoteBenchmarkResponse(BaseResponse):
    date: str
    benchmark: int


class FamaFrench(BaseResponse):
    date: str
    value: float
    size: float
    momentum: float
    market_excess: float
    risk_free: float
    market: int
    id: int


class FamaFrenchTimeSeriesResponse(BasePaginatedResponse):
    results: List[FamaFrench]


def test_filter_remote_models(requests_mock):
    """Test remote models

    Args:
        requests_mock (_type_): Requests mock
    """

    with open("tests/data/mock_benchmarks_states.json") as f:
        mock_benchmarks_states_response = json.load(f)

    requests_mock.get(
        "http://benchmarks-api.noviscient.com/api/v1/benchmarks-states/",
        json=mock_benchmarks_states_response,
    )

    remote_benchmarks = RemoteModel(
        base_url="http://benchmarks-api.noviscient.com/api/v1/"
    )

    response = remote_benchmarks.filter(
        entity="benchmarks-states",
        response_class=RemoteBenchmarkStatesResponse,
    )

    assert (
        type(response) == RemoteBenchmarkStatesResponse
    ), f"Response type is not {RemoteBenchmarkStatesResponse}"
    assert len(response.results) == 6, "Response results length is not 6"
    assert response.count == 6, "Response count is not 6"


def test_filter_remote_models_with_exception(requests_mock):
    """Test remote models exception

    Args:
        requests_mock (_type_): Requests mock
    """

    requests_mock.get(
        "http://benchmarks-api.noviscient.com/api/v1/benchmarks-states/",
        exc=GenericFailedRequest("Failed request"),
    )

    remote_benchmarks = RemoteModel(
        base_url="http://benchmarks-api.noviscient.com/api/v1/"
    )

    with pytest.raises(GenericFailedRequest):
        remote_benchmarks.filter(
            entity="benchmarks-states",
            response_class=RemoteBenchmarkStatesResponse,
        )


def test_create_remote_models(requests_mock):
    """Test save remote models

    Args:
        requests_mock (_type_): Requests mock
    """

    with open("tests/data/mock_save_benchmark_timeseries_response.json") as f:
        mock_response = json.load(f)

    requests_mock.post(
        "http://benchmarks-api.noviscient.com/api/v1/benchmark-timeseries/",
        json=mock_response,
    )

    remote_benchmarks = RemoteModel(
        base_url="http://benchmarks-api.noviscient.com/api/v1/"
    )

    save_response: RemoteBenchmarkResponse = remote_benchmarks.create(
        entity="benchmark-timeseries",
        response_class=RemoteBenchmarkResponse,
        data="2022-10-11",
        benchmark=1,
    )

    assert save_response.benchmark == 0
    assert save_response.date == "2022-10-27"


def test_filter_remote_famafrench_timeseries_models(requests_mock):
    """Test remote models

    Args:
        requests_mock (_type_): Requests mock
    """

    with open("tests/data/mock_famafrench_timeseries.json") as f:
        mock_ff_timeseries_response = json.load(f)

    requests_mock.get(
        "http://benchmarks-api.noviscient.com/api/v1/famafrench-timeseries/",
        json=mock_ff_timeseries_response,
    )

    remote_benchmarks = RemoteModel(
        base_url="http://benchmarks-api.noviscient.com/api/v1/"
    )

    response = remote_benchmarks.filter_all(
        entity="famafrench-timeseries",
        response_class=FamaFrenchTimeSeriesResponse,
    )

    assert (
        type(response) == FamaFrenchTimeSeriesResponse
    ), f"Response type is not {FamaFrenchTimeSeriesResponse}"
    assert len(response.results) == 304, "Response results length is not 304"
    assert response.count == 304, "Response count is not 304"


def test_successful_delete_remote_models(requests_mock):
    """Test successful delete remote models

    Args:
        requests_mock (_type_): Requests mock
    """

    requests_mock.delete(
        "http://benchmarks-api.noviscient.com/api/v1/benchmark-timeseries/12345/",
        content=b"",
        status_code=codes.no_content,
    )

    remote_benchmarks = RemoteModel(
        base_url="http://benchmarks-api.noviscient.com/api/v1/"
    )

    response = remote_benchmarks.delete(
        entity="benchmark-timeseries/12345",
        response_class=BaseResponse,
    )

    assert (
        type(response) == BaseResponse
    ), f"Expected response type is {BaseResponse}, got {type(response)}"

    assert (
        response.http_response.status_code == codes.no_content
    ), f"Expected status code is {codes.no_content}, got {response.http_response.status_code}"


def test_failed_delete_remote_models(requests_mock):
    """Test failed delete remote models

    Args:
        requests_mock (_type_): Requests mock
    """

    requests_mock.delete(
        "http://benchmarks-api.noviscient.com/api/v1/benchmark-timeseries/12345/",
        json={"detail": "Not found"},
        status_code=codes.not_found,
    )

    remote_benchmarks = RemoteModel(
        base_url="http://benchmarks-api.noviscient.com/api/v1/"
    )

    with pytest.raises(GenericFailedRequest):
        remote_benchmarks.delete(
            entity="benchmark-timeseries/12345",
            response_class=BaseResponse,
        )
