from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

import requests
from pydantic import BaseModel, ValidationError
from requests import Response

from .errors import ApiError, ConfigError
from .models import ReportData, StatusReport, WeightByDate
from .settings import get_config

DEFAULT_TIMEOUT_SECONDS = 15


def get_status(access_token: str) -> StatusReport:
    payload = _send_request('GET', 'api/status', access_token=access_token).json()
    return _parse_response(payload, StatusReport, 'status')


def get_weight_data(date_from: str | None, date_to: str | None, access_token: str) -> ReportData:
    params = _build_params(date_from=date_from, date_to=date_to)
    payload = _send_request('GET', 'api/weight', params=params, access_token=access_token).json()
    return _parse_response(payload, ReportData, 'report')


def get_weight_data_by_date(date: str, access_token: str) -> WeightByDate:
    payload = _send_request('GET', f'api/weight/{date}', access_token=access_token).json()
    return _parse_response(payload, WeightByDate, 'weight-by-date')


def add_weight_data(date: str | None, weight: float, access_token: str) -> None:
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    data = {'date': date, 'weight': weight}
    _send_request('POST', 'api/weight', data=data, access_token=access_token)


def update_weight_data(date: str, weight: float, access_token: str) -> None:
    data = {'weight': weight}
    _send_request('PUT', f'api/weight/{date}', data=data, access_token=access_token)


def delete_weight_data(date: str, access_token: str) -> None:
    _send_request('DELETE', f'api/weight/{date}', access_token=access_token)


def _send_request(
    method: str,
    url: str,
    *,
    data: dict[str, object] | None = None,
    params: dict[str, str] | None = None,
    access_token: str | None = None,
) -> Response:
    headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
    resolved_url = _resolve_url(url)

    try:
        response = requests.request(
            method,
            resolved_url,
            json=data,
            params=params,
            headers=headers or None,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise ApiError(f'Server responded with an error: {exc}') from exc
    except requests.exceptions.RequestException as exc:
        raise ApiError(f'Could not reach the server: {exc}') from exc

    return response


def _resolve_url(url: str) -> str:
    if _is_absolute_url(url):
        return url

    base_url = get_config().api.base_url.strip()

    if not base_url:
        raise ConfigError("Missing 'base_url' in api configuration.")

    if not _is_absolute_url(base_url):
        raise ConfigError("Invalid 'base_url' in api configuration. It must include http or https.")

    return f'{base_url.rstrip("/")}/{url.lstrip("/")}'


def _is_absolute_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)


def _build_params(**params: str | None) -> dict[str, str] | None:
    cleaned = {key: value for key, value in params.items() if value is not None}
    return cleaned or None


def _parse_response[T: BaseModel](payload: object, model: type[T], label: str) -> T:
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise ApiError(f'Invalid {label} response payload.') from exc
