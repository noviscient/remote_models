# Development environment

## Install packages

### Install requirements-dev.txt

```sh
> pip install -r requirements-dev.txt
> pre-commit install
```

### Install remote_models

```sh
> pip install -e .
```

### Run tests

```sh
pytest
```

# How to install in the project

```sh
> pip install git+https://github.com/noviscient/remote_models.git
```

# Examples

```python

remote_benchmarks_model = RemoteModel(
    base_url="https://api.com/"
)

data = {
    "benchmark": result.benchmark.id,
    "date": item.date,
    "adjusted_close": item.adjusted_close,
}

response : Type[BaseResponse] = remote_benchmarks_model.save(
    entity="benchmark-timeseries",
    response_class=BenchmarkTimeseriesResponse,
    **data,
)
```