import requests
import jsonschema
import json
import logging

from urllib.parse import urljoin
from typing import Dict, TypeVar
from collections import deque

T = TypeVar('T')


__all__ = [
    'Chain',
]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def lazy_compatible(f):
    def wrapped(self, *args, **kwargs):
        if self._lazy:
            self.task.append((f, self, args, kwargs))
            return self
        else:
            return f(self, *args, **kwargs)
    return wrapped


class Context:
    def __init__(self):
        self.request_data: Dict[str, T] = {}
        self.url_params: Dict[str, str] = {}
        self.request_data_raw: str = None
        self.headers: Dict[str, T] = {}
        self.cookies: Dict[str, T] = {}
        self.response = None
        self.response_data: Dict[str, T] = None
        self.response_data_raw: str = None
        self.status_code: int = None

    def __str__(self) -> str:
        return f"[\n\tRequest data raw: {self.request_data_raw}\n" \
               f"\tUrl params: {self.url_params}\n" \
               f"\tHeaders: {self.headers}\n" \
               f"\tCookies: {self.cookies}\n" \
               f"\tResponse data: {self.response_data}\n" \
               f"\tResponse data raw: {self.response_data_raw}\n" \
               f"\tStatus code: {self.status_code}\n]"

    def clear(self):
        self.response, self.response_data, self.response_data_raw, self.status_code = None, None, None, None


class Pipeline:
    def __init__(self, host, port="80", url_prefix="/", protocol='http') -> None:
        self.context: Context = Context()
        self.protocol = protocol
        self.host = host
        self.port = port
        self.session: requests.Session = requests.Session()
        self.url_prefix = url_prefix
        self.base_http_path = urljoin(f"{self.protocol}://{self.host}:{self.port}", self.url_prefix)
        self.task: deque = deque()
        self._lazy: bool = False

    def execute(self):
        while len(self.task) > 0:
            f = self.task.popleft()
            logging.debug(f"Executing {f[0].__name__}...")
            f[0](f[1], *f[2], **f[3])
        self._lazy = False
        return self

    def lazy(self):
        self._lazy = True
        return self


class DoPrepareData(Pipeline):
    @lazy_compatible
    def do_prepare_data_url_params(self, params_dict: Dict) -> 'DoPrepareData':
        self.context.url_params = params_dict
        return self

    @lazy_compatible
    def do_prepare_data_json(self, json_data_dict: Dict) -> 'DoPrepareData':
        self.context.request_data = json_data_dict
        self.context.request_data_raw = json.dumps(self.context.request_data)
        return self

    @lazy_compatible
    def do_prepare_update_data_json(self, new_data: dict) -> 'DoPrepareData':
        self.context.request_data.update(new_data)
        self.context.request_data_raw = json.dumps(self.context.request_data)
        return self


class DoPrepareRequest(Pipeline):
    @lazy_compatible
    def do_prepare_request(self, headers=None, cookies=None) -> 'DoPrepareRequest':
        self.context.headers = headers
        self.context.cookies = cookies
        logging.debug(self.context)
        return self


class DoRequest(Pipeline):
    def __finalize_request(self) -> None:
        try:
            self.context.response_data = self.context.response.json()
        except json.JSONDecodeError:
            logging.error("No json in response or json is incorrect")
        self.context.response_data_raw = self.context.response.text.replace("\n", "")
        self.context.status_code = self.context.response.status_code
        logging.debug(self.context)

    @lazy_compatible
    def do_request_get(self, api_path, **kwargs) -> 'DoRequest':
        self.context.clear()
        self.context.response = self.session.get(
            urljoin(self.base_http_path, api_path),
            params=self.context.url_params,
            headers=self.context.headers,
            cookies=self.context.cookies,
            **kwargs
        )
        self.__finalize_request()
        return self

    @lazy_compatible
    def do_request_post(self, api_path, **kwargs) -> 'DoRequest':
        self.context.clear()
        self.context.response = self.session.post(
            urljoin(self.base_http_path, api_path),
            data=self.context.request_data_raw,
            headers=self.context.headers,
            cookies=self.context.cookies,
            params=self.context.url_params,
            **kwargs
        )
        self.__finalize_request()
        return self

    @lazy_compatible
    def do_request_patch(self, api_path, **kwargs) -> 'DoRequest':
        self.context.clear()
        self.context.response = self.session.patch(
            urljoin(self.base_http_path, api_path),
            data=self.context.request_data_raw,
            headers=self.context.headers,
            cookies=self.context.cookies,
            params=self.context.url_params,
            **kwargs
        )
        self.__finalize_request()
        return self

    @lazy_compatible
    def do_request_delete(self, api_path, **kwargs) -> 'DoRequest':
        self.context.clear()
        self.context.response = self.session.delete(
            urljoin(self.base_http_path, api_path),
            headers=self.context.headers,
            cookies=self.context.cookies,
            params=self.context.url_params,
            **kwargs
        )
        self.__finalize_request()
        return self


class DoValidate(Pipeline):
    @lazy_compatible
    def do_validate_schema(self, schema) -> 'DoValidate':
        jsonschema.validate(self.context.response_data, schema)
        return self

    @lazy_compatible
    def do_validate_response_code(self, expected_status_code: int) -> 'DoValidate':
        assert expected_status_code == self.context.status_code
        return self


class Chain(DoPrepareRequest, DoPrepareData, DoRequest, DoValidate):
    pass
