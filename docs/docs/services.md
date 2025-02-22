## Services

Services must be placed inside `app/services/` directory. The project already provides the following services:

### HTTP

Its an HTTP client. Usefull when you have to call external API's or other services. By default, it'll retry up to 5 times if the request fails.

```python
from services import http

async def test():
    result = await http.get(url="https://google.com")
```

### Logger

A logger ready to be used.

```python
from services import logger

async def test():
    logger.debug("cool!")
```

### Settings

Access your project settings from any part of your code. Remember that settings are defined on `settings.py` -> `Settings` class.  Any class attribute defined in `Settings` class can be overrided on *.env* file  

```python
from services import settings

async def test():
    return settings.HOST + ":" + settings.PORT
```
