import json
from typing import Any, Dict, List

import pytest

from remote_models.exceptions import GenericFailedRequest
from remote_models.models import RemoteModel
from remote_models.responses import BaseResponse


class RemoteBenchmarkStatesResponse(BaseResponse):
    results: List[Dict[str, Any]]


def test_remote_models(requests_mock):
    """Test remote models

    Args:
        requests_mock (_type_): Requests mock
    """

    with open("tests/data/mock_benchmarks_states.json") as f:
        mock_benchmarks_states_response = json.load(f)

    requests_mock.get(
        "http://benchmarks-api.noviscient.com/api/v1/benchmarks-states",
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


def test_remote_models_with_exception(requests_mock):
    """Test remote models exception

    Args:
        requests_mock (_type_): Requests mock
    """

    requests_mock.get(
        "http://benchmarks-api.noviscient.com/api/v1/benchmarks-states",
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
