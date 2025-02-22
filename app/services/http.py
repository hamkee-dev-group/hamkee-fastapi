import httpx
from httpx import Response
from services import logger
from result import Result, Ok, Err

_DEFAULT_TIMEOUT = 5  # five seconds max timeout
_MAX_RETRIES = 5

_client = None
_retryable_errors = (
    httpx.ConnectTimeout,
    httpx.RemoteProtocolError,
    httpx.ReadTimeout,
)


async def get(
    url: str, headers: dict = None, timeout: int = _DEFAULT_TIMEOUT
) -> Result[Response, str]:
    """Send a GET request.

    Args:
        url (str): The URL to send the request to.
        headers (dict): The headers to send in the request. Defaults to None.
        timeout (int): The timeout for the request. Defaults to _DEFAULT_TIMEOUT.
    Returns:
        A Result object with the response or the last exception formatted as a string.
    """
    return await _retryable_request("get", url, headers=headers, timeout=timeout)


async def post(
    url: str,
    data: dict = None,
    json: dict = None,
    headers: dict = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> Result[Response, str]:
    """Send a POST request.

    Args:
        url (str): The URL to send the request to.
        data (dict): The data to send in the request body. Defaults to None.
        json (dict): The JSON to send in the request body. Defaults to None.
        headers (dict): The headers to send in the request. Defaults to None.
        timeout (int): The timeout for the request. Defaults to _DEFAULT_TIMEOUT.

    Returns:
        A Result object with the response or the last exception formatted as a string.
    """
    return await _retryable_request(
        "post", url, data=data, json=json, headers=headers, timeout=timeout
    )


async def put(
    url: str,
    data: dict = None,
    json: dict = None,
    headers: dict = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> Result[Response, str]:
    """Send a PUT request.

    Args:
        url (str): The URL to send the request to.
        data (dict): The data to send in the request body. Defaults to None.
        json (dict): The JSON to send in the request body. Defaults to None.
        headers (dict): The headers to send in the request. Defaults to None.
        timeout (int): The timeout for the request. Defaults to _DEFAULT_TIMEOUT.

    Returns:
        A Result object with the response or the last exception formatted as a string.
    """
    return await _retryable_request(
        "put", url, data=data, json=json, headers=headers, timeout=timeout
    )


async def init_pool():
    """Init HTTPX AsyncClient thread pool."""
    await _get_client()
    logger.info("Started httpx async clients thread pool.")


async def close_pool():
    """Close HTTPX AsyncClient thread pool."""
    client = await _get_client()
    await client.aclose()
    global _client
    _client = None
    logger.info("Closed httpx async clients thread pool.")


async def _retryable_request(
    method: str,
    url: str,
    data: dict = None,
    json: dict = None,
    headers: dict = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> Result[Response, str]:
    """Send a request with retries.

    If the request fails, retry it up to _MAX_RETRIES times.
    If the request fails after _MAX_RETRIES times, return the last exception formatted
    as a string and wrapped as an Err.

    Args:
        method (str): The HTTP method to use.
        url (str): The URL to send the request to.
        data (dict): The data to send in the request body. Defaults to None.
        json (dict): The JSON to send in the request body. Defaults to None.
        headers (dict): The headers to send in the request. Defaults to None.
        timeout (int): The timeout for the request. Defaults to _DEFAULT_TIMEOUT.

    Raises:
        ValueError: If the method is invalid.

    Returns:
        A Result object with the response or the last exception formatted as a string.
    """
    client = await _get_client()

    fn = getattr(client, method)
    params = await _get_params(method, data, json, headers, timeout)
    logger.debug(f"Sending {method} request to: {url} with params {params}")

    last_error = ""

    for i in range(0, _MAX_RETRIES):
        try:
            response = await fn(url, **params)
            return Ok(response)
        except _retryable_errors as e:
            logger.debug(
                f"Retry count ({i}): {method.upper()} -> {url} params: {params}"
            )
            if i == _MAX_RETRIES - 1:
                last_error = e.format_exc()  # type: ignore
            continue

    logger.error(
        f"Failed to send {method} request to {url} with params {params}: {last_error}"
    )
    return Err(last_error)


async def _get_params(
    method: str,
    data: dict = None,
    json: dict = None,
    headers: dict = None,
    timeout: int = None,
) -> dict:
    """Get the parameters for the request.
    
    Args:
        method (str): The HTTP method to use.
        data (dict): The data to send in the request body. Defaults to None.
        json (dict): The JSON to send in the request body. Defaults to None.
        headers (dict): The headers to send in the request. Defaults to None.
        timeout (int): The timeout for the request. Defaults to None.

    Returns:
        A dictionary with the parameters for the request.
    """
    params = {"headers": headers, "timeout": timeout}
    if method == "post":
        params["data"] = data
        params["json"] = json
    return params


async def _get_client() -> httpx.AsyncClient:
    """Get the HTTPX AsyncClient. If it doesn't exist, create it."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(verify=False)
    return _client
