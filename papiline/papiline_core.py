import requests
import jsonschema
import json
import logging

from urllib.parse import urljoin
from faker.providers import BaseProvider
from typing import Dict, TypeVar

T = TypeVar('T')


__all__ = [
    'Pipeline',
]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


class Context:
    request_data: Dict[str, T] = {}
    request_data_raw: str = None
    headers: Dict[str, T] = {}
    cookies: Dict[str, T] = {}
    response = None
    response_data: Dict[str, T] = None
    response_data_raw: str = None
    status_code: int = None
    faker_instance: BaseProvider = None
    host: str = None
    port: str = None
    protocol: str = "http"
    url_prefix: str = None
    base_http_path: str = None

    def __str__(self) -> str:
        return f"[\n\tRequest data raw: {self.request_data_raw}\n" \
               f"\tHeaders: {self.headers}\n" \
               f"\tCookies: {self.cookies}\n" \
               f"\tProtocol: {self.protocol}\n" \
               f"\tHost: {self.host}\n" \
               f"\tPort: {self.port}\n" \
               f"\tUrl Prefix: {self.url_prefix}\n" \
               f"\tResponse data: {self.response_data}\n" \
               f"\tResponse data raw: {self.response_data_raw}\n" \
               f"\tStatus code: {self.status_code}\n]"


class DoPrepareData(Context):
    def do_prepare_data_json(self, json_data_dict: Dict) -> 'DoPrepareData':
        self.request_data = json_data_dict
        self.request_data_raw = json.dumps(self.request_data)
        return self

    def do_prepare_update_data_json(self, new_data: dict) -> 'DoPrepareData':
        self.request_data.update(new_data)
        self.request_data_raw = json.dumps(self.request_data)
        return self


class DoPrepareRequest(Context):
    def do_prepare_request(self, headers=None, cookies=None) -> 'DoPrepareRequest':
        self.headers = headers
        self.cookies = cookies
        logging.debug(self)
        return self


class DoRequest(Context):
    def __finalize_request(self) -> None:
        try:
            self.response_data = self.response.json()
        except json.JSONDecodeError:
            logging.error("No json in response or json is incorrect")
        self.response_data_raw = self.response.text.replace("\n", "")
        self.status_code = self.response.status_code
        logging.debug(self)

    def do_request_get(self, api_path, **kwargs) -> 'DoRequest':
        self.response = requests.get(
            urljoin(self.base_http_path, api_path),
            params=self.request_data_raw,
            headers=self.headers,
            cookies=self.cookies,
            **kwargs
        )
        self.__finalize_request()
        return self

    def do_request_post(self, api_path, **kwargs) -> 'DoRequest':
        self.response = requests.post(
            urljoin(self.base_http_path, api_path),
            data=self.request_data_raw,
            headers=self.headers,
            cookies=self.cookies,
            **kwargs
        )
        self.__finalize_request()
        return self

    def do_request_patch(self, api_path, **kwargs) -> 'DoRequest':
        self.response = requests.patch(
            urljoin(self.base_http_path, api_path),
            data=self.request_data_raw,
            headers=self.headers,
            cookies=self.cookies,
            **kwargs
        )
        self.__finalize_request()
        return self

    def do_request_delete(self, api_path, **kwargs) -> 'DoRequest':
        self.response = requests.delete(
            urljoin(self.base_http_path, api_path),
            headers=self.headers,
            cookies=self.cookies,
            **kwargs
        )
        self.__finalize_request()
        return self


class DoValidate(Context):
    def do_validate_schema(self, schema) -> 'DoValidate':
        jsonschema.validate(self.response_data, schema)
        return self

    def do_validate_response_code(self, expected_status_code: int) -> 'DoValidate':
        assert expected_status_code == self.status_code
        return self


class Pipeline(DoPrepareData, DoPrepareRequest, DoRequest, DoValidate):
    def do_pipeline_init(self, host, protocol="http", port="80", url_prefix="/") -> 'Pipeline':
        self.protocol = protocol
        self.host = host
        self.port = port
        self.url_prefix = url_prefix
        self.base_http_path = urljoin(f"{self.protocol}://{self.host}:{self.port}", self.url_prefix)
        return self

