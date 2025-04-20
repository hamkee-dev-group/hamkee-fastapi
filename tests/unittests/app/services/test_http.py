import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from result import Ok, Err

from app.services.http import (
    HTTPClient,
    HTTPClientConfig,
    get,
    post,
    put,
    delete,
    init_pool,
    close_pool,
)


@pytest.fixture
def mock_response():
    """Create a mock httpx.Response object."""
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = 200
    mock.json.return_value = {"data": "test"}
    return mock


@pytest.fixture
def mock_client():
    """Create a mock for httpx.AsyncClient."""
    mock = AsyncMock(spec=httpx.AsyncClient)
    mock.get.return_value = MagicMock(spec=httpx.Response)
    mock.post.return_value = MagicMock(spec=httpx.Response)
    mock.put.return_value = MagicMock(spec=httpx.Response)
    mock.delete.return_value = MagicMock(spec=httpx.Response)
    mock.aclose = AsyncMock()
    return mock


class TestHTTPClientConfig:
    def test_default_config(self):
        """Test HTTPClientConfig initializes with default values."""
        config = HTTPClientConfig()
        assert config.default_timeout == 5
        assert config.max_retries == 5
        assert config.verify_ssl is True
        assert httpx.ConnectTimeout in config.retryable_exceptions
        assert httpx.ReadTimeout in config.retryable_exceptions
        assert httpx.RemoteProtocolError in config.retryable_exceptions

    def test_custom_config(self):
        """Test HTTPClientConfig can be initialized with custom values."""
        custom_exceptions = (ValueError, TypeError)
        config = HTTPClientConfig(
            default_timeout=10,
            max_retries=3,
            verify_ssl=False,
            retryable_exceptions=custom_exceptions,
        )
        assert config.default_timeout == 10
        assert config.max_retries == 3
        assert config.verify_ssl is False
        assert config.retryable_exceptions == custom_exceptions


class TestHTTPClient:
    @pytest.mark.asyncio
    async def test_get_client_creates_client_if_none(self):
        """Test get_client() creates a new client if none exists."""
        with patch("app.services.http.AsyncClient") as mock_async_client:
            client = HTTPClient()
            await client.get_client()
            mock_async_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_returns_existing_client(self, mock_client):
        """Test get_client() returns existing client if already created."""
        client = HTTPClient(client=mock_client)
        result = await client.get_client()
        assert result is mock_client

    @pytest.mark.asyncio
    async def test_get(self, mock_client, mock_response):
        """Test GET request is properly forwarded to client."""
        mock_client.get.return_value = mock_response
        client = HTTPClient(client=mock_client)

        result = await client.get("https://example.com", headers={"X-Test": "test"})

        mock_client.get.assert_called_once_with(
            "https://example.com", headers={"X-Test": "test"}, timeout=5
        )
        assert isinstance(result, Ok)
        assert result.ok_value == mock_response

    @pytest.mark.asyncio
    async def test_post(self, mock_client, mock_response):
        """Test POST request is properly forwarded to client."""
        mock_client.post.return_value = mock_response
        client = HTTPClient(client=mock_client)

        result = await client.post(
            "https://example.com",
            json={"test": "data"},
            headers={"Content-Type": "application/json"},
        )

        mock_client.post.assert_called_once_with(
            "https://example.com",
            data=None,
            json={"test": "data"},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert isinstance(result, Ok)
        assert result.ok_value == mock_response

    @pytest.mark.asyncio
    async def test_put(self, mock_client, mock_response):
        """Test PUT request is properly forwarded to client."""
        mock_client.put.return_value = mock_response
        client = HTTPClient(client=mock_client)

        result = await client.put("https://example.com", data={"test": "data"})

        mock_client.put.assert_called_once_with(
            "https://example.com",
            data={"test": "data"},
            json=None,
            headers=None,
            timeout=5,
        )
        assert isinstance(result, Ok)
        assert result.ok_value == mock_response

    @pytest.mark.asyncio
    async def test_delete(self, mock_client, mock_response):
        """Test DELETE request is properly forwarded to client."""
        mock_client.delete.return_value = mock_response
        client = HTTPClient(client=mock_client)

        result = await client.delete("https://example.com")

        mock_client.delete.assert_called_once_with(
            "https://example.com", headers=None, timeout=5
        )
        assert isinstance(result, Ok)
        assert result.ok_value == mock_response

    @pytest.mark.asyncio
    async def test_close(self, mock_client):
        """Test close() properly closes the client."""
        client = HTTPClient(client=mock_client)
        await client.close()
        mock_client.aclose.assert_called_once()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_retry_behavior(self, mock_client):
        """Test retry behavior when exceptions are raised."""
        # Setup mock to raise exceptions for the first 2 attempts then succeed
        mock_client.get.side_effect = [
            httpx.ConnectTimeout("Connection timeout"),
            httpx.ReadTimeout("Read timeout"),
            MagicMock(spec=httpx.Response),
        ]

        config = HTTPClientConfig(max_retries=3)
        client = HTTPClient(client=mock_client, config=config)

        result = await client.get("https://example.com")

        # Should have been called exactly 3 times (2 failures, 1 success)
        assert mock_client.get.call_count == 3
        assert isinstance(result, Ok)

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, mock_client):
        """Test behavior when max retries is exceeded."""
        mock_client.get.side_effect = httpx.ConnectTimeout("Connection timeout")

        config = HTTPClientConfig(max_retries=3)
        client = HTTPClient(client=mock_client, config=config)

        result = await client.get("https://example.com")

        assert mock_client.get.call_count == 3
        assert isinstance(result, Err)
        assert "Failed to GET https://example.com after 3 attempts" in result.err_value


class TestModuleFunctions:
    @pytest.mark.asyncio
    async def test_get(self):
        """Test get() function delegates to default client."""
        with patch("app.services.http.default_client.get") as mock_get:
            mock_get.return_value = Ok(MagicMock(spec=httpx.Response))
            await get("https://example.com")
            mock_get.assert_called_once_with(
                url="https://example.com", headers=None, timeout=None
            )

    @pytest.mark.asyncio
    async def test_post(self):
        """Test post() function delegates to default client."""
        with patch("app.services.http.default_client.post") as mock_post:
            mock_post.return_value = Ok(MagicMock(spec=httpx.Response))
            await post(
                "https://example.com",
                json={"data": "test"},
                headers={"Content-Type": "application/json"},
            )
            mock_post.assert_called_once_with(
                url="https://example.com",
                data=None,
                json={"data": "test"},
                headers={"Content-Type": "application/json"},
                timeout=None,
            )

    @pytest.mark.asyncio
    async def test_put(self):
        """Test put() function delegates to default client."""
        with patch("app.services.http.default_client.put") as mock_put:
            mock_put.return_value = Ok(MagicMock(spec=httpx.Response))
            await put("https://example.com", data={"key": "value"})
            mock_put.assert_called_once_with(
                url="https://example.com",
                data={"key": "value"},
                json=None,
                headers=None,
                timeout=None,
            )

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test delete() function delegates to default client."""
        with patch("app.services.http.default_client.delete") as mock_delete:
            mock_delete.return_value = Ok(MagicMock(spec=httpx.Response))
            await delete("https://example.com")
            mock_delete.assert_called_once_with(
                url="https://example.com", headers=None, timeout=None
            )

    @pytest.mark.asyncio
    async def test_init_pool(self):
        """Test init_pool() initializes the default client."""
        with patch("app.services.http.default_client.get_client") as mock_get_client:
            await init_pool()
            mock_get_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_pool(self):
        """Test close_pool() closes the default client."""
        with patch("app.services.http.default_client.close") as mock_close:
            await close_pool()
            mock_close.assert_called_once()
