import json
from typing import Any, Dict, List

import pytest

from remote_models.exceptions import GenericFailedRequest
from remote_models.models import RemoteModel
from remote_models.responses import BasePaginatedResponse, BaseResponse


class RemoteBenchmarkStatesResponse(BasePaginatedResponse):
    results: List[Dict[str, Any]]


class RemoteBenchmarkResponse(BaseResponse):
    date: str
    benchmark: int


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


def test_save_remote_models(requests_mock):
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

    save_response: RemoteBenchmarkResponse = remote_benchmarks.save(
        entity="benchmark-timeseries",
        response_class=RemoteBenchmarkResponse,
        data="2022-10-11",
        benchmark=1,
    )

    assert save_response.benchmark == 0
    assert save_response.date == "2022-10-27"
