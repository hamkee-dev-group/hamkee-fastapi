"""HTTP client service for making HTTP requests with automatic retries.

This module provides a clean, testable HTTP client implementation that
wraps httpx with retry capabilities and proper error handling.
"""

from typing import Any, Dict, Optional, Tuple, Type, TypeVar

import httpx
from httpx import AsyncClient, Response
from result import Err, Ok, Result

from app.services import logger

# Type variable for generic return type
T = TypeVar("T", bound=Response)


class HTTPClientConfig:
    """Configuration class for HTTPClient.

    Attributes:
        default_timeout: Default timeout for HTTP requests in seconds.
        max_retries: Maximum number of retry attempts for failed requests.
        verify_ssl: Whether to verify SSL certificates.
        retryable_exceptions: Tuple of exception types that should trigger a retry.
    """

    def __init__(
        self,
        default_timeout: int = 5,
        max_retries: int = 5,
        verify_ssl: bool = True,
        retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    ):
        """Initialize HTTPClientConfig.

        Args:
            default_timeout: Default timeout for requests in seconds. Defaults to 5.
            max_retries: Maximum number of retry attempts. Defaults to 5.
            verify_ssl: Whether to verify SSL certificates. Defaults to True.
            retryable_exceptions: Exception types that trigger retries.
                Defaults to connection and timeout exceptions.
        """
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl

        if retryable_exceptions is None:
            self.retryable_exceptions = (
                httpx.ConnectTimeout,
                httpx.RemoteProtocolError,
                httpx.ReadTimeout,
            )
        else:
            self.retryable_exceptions = retryable_exceptions


class HTTPClient:
    """HTTP client for making requests with automatic retries.

    This class provides methods for making HTTP requests with built-in retry
    functionality and consistent error handling.
    """

    def __init__(
        self,
        client: Optional[AsyncClient] = None,
        config: Optional[HTTPClientConfig] = None,
    ):
        """Initialize HTTPClient.

        Args:
            client: An existing httpx.AsyncClient instance. If None, a new client
                will be created using the provided config.
            config: Configuration for the HTTP client. If None, default config is used.
        """
        self.config = config or HTTPClientConfig()
        self._client = client

    async def get_client(self) -> AsyncClient:
        """Get the AsyncClient instance, creating one if needed.

        Returns:
            An httpx.AsyncClient instance.
        """
        if self._client is None:
            self._client = AsyncClient(verify=self.config.verify_ssl)
        return self._client

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Result[Response, str]:
        """Send a GET request.

        Args:
            url: The URL to send the request to.
            headers: The headers to send in the request.
            timeout: The timeout for the request. Uses default_timeout if None.

        Returns:
            A Result containing either the Response or an error message.
        """
        return await self._send_request(
            method="get",
            url=url,
            headers=headers,
            timeout=timeout or self.config.default_timeout,
        )

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Result[Response, str]:
        """Send a POST request.

        Args:
            url: The URL to send the request to.
            data: Form data to send in the request body.
            json: JSON data to send in the request body.
            headers: The headers to send in the request.
            timeout: The timeout for the request. Uses default_timeout if None.

        Returns:
            A Result containing either the Response or an error message.
        """
        return await self._send_request(
            method="post",
            url=url,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout or self.config.default_timeout,
        )

    async def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Result[Response, str]:
        """Send a PUT request.

        Args:
            url: The URL to send the request to.
            data: Form data to send in the request body.
            json: JSON data to send in the request body.
            headers: The headers to send in the request.
            timeout: The timeout for the request. Uses default_timeout if None.

        Returns:
            A Result containing either the Response or an error message.
        """
        return await self._send_request(
            method="put",
            url=url,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout or self.config.default_timeout,
        )

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Result[Response, str]:
        """Send a DELETE request.

        Args:
            url: The URL to send the request to.
            headers: The headers to send in the request.
            timeout: The timeout for the request. Uses default_timeout if None.

        Returns:
            A Result containing either the Response or an error message.
        """
        return await self._send_request(
            method="delete",
            url=url,
            headers=headers,
            timeout=timeout or self.config.default_timeout,
        )

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("Closed HTTP client.")

    async def _send_request(
        self, method: str, url: str, **kwargs: Any
    ) -> Result[Response, str]:
        """Send an HTTP request with retry functionality.

        If the request fails with a retryable exception, it will be retried
        up to max_retries times before returning an error.

        Args:
            method: HTTP method (get, post, put, delete, etc.)
            url: URL to send the request to
            **kwargs: Additional arguments to pass to the request

        Returns:
            A Result containing either the Response or an error message.
        """
        client = await self.get_client()
        request_func = getattr(client, method)

        logger.debug(f"Sending {method.upper()} request to: {url} with params {kwargs}")

        last_error = ""

        for attempt in range(self.config.max_retries):
            try:
                response = await request_func(url, **kwargs)
                return Ok(response)
            except self.config.retryable_exceptions as e:
                logger.debug(
                    f"Retry attempt {attempt + 1}/{self.config.max_retries}: "
                    f"{method.upper()} -> {url}"
                )
                if attempt == self.config.max_retries - 1:
                    # This is the last attempt
                    last_error = str(e)

        error_message = f"Failed to {method.upper()} {url} after {self.config.max_retries} attempts: {last_error}"
        logger.error(error_message)
        return Err(error_message)


# Default client instance for convenience
default_config = HTTPClientConfig()
default_client = HTTPClient(config=default_config)


# Convenience functions that use the default client
async def get(
    url: str, headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None
) -> Result[Response, str]:
    """Send a GET request using the default HTTP client.

    Args:
        url: The URL to send the request to.
        headers: The headers to send in the request.
        timeout: The timeout for the request. Uses default_timeout if None.

    Returns:
        A Result containing either the Response or an error message.
    """
    return await default_client.get(url=url, headers=headers, timeout=timeout)


async def post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
) -> Result[Response, str]:
    """Send a POST request using the default HTTP client.

    Args:
        url: The URL to send the request to.
        data: Form data to send in the request body.
        json: JSON data to send in the request body.
        headers: The headers to send in the request.
        timeout: The timeout for the request. Uses default_timeout if None.

    Returns:
        A Result containing either the Response or an error message.
    """
    return await default_client.post(
        url=url, data=data, json=json, headers=headers, timeout=timeout
    )


async def put(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
) -> Result[Response, str]:
    """Send a PUT request using the default HTTP client.

    Args:
        url: The URL to send the request to.
        data: Form data to send in the request body.
        json: JSON data to send in the request body.
        headers: The headers to send in the request.
        timeout: The timeout for the request. Uses default_timeout if None.

    Returns:
        A Result containing either the Response or an error message.
    """
    return await default_client.put(
        url=url, data=data, json=json, headers=headers, timeout=timeout
    )


async def delete(
    url: str, headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None
) -> Result[Response, str]:
    """Send a DELETE request using the default HTTP client.

    Args:
        url: The URL to send the request to.
        headers: The headers to send in the request.
        timeout: The timeout for the request. Uses default_timeout if None.

    Returns:
        A Result containing either the Response or an error message.
    """
    return await default_client.delete(url=url, headers=headers, timeout=timeout)


async def init_pool() -> None:
    """Initialize the default HTTP client pool."""
    await default_client.get_client()
    logger.info("Started HTTP client pool.")


async def close_pool() -> None:
    """Close the default HTTP client pool."""
    await default_client.close()
    logger.info("Closed HTTP client pool.")
