import logging
import httpx
from typing import Dict, List, Any
from app.config import settings

logger = logging.getLogger(__name__)


class HTTPClient:
    def __init__(self):
        self.timeout = settings.http_timeout
        self.max_redirects = settings.http_max_redirects
    
    async def fetch_metadata(self, url: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=self.max_redirects,
            verify=settings.http_verify_ssl
        ) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                headers: Dict[str, str] = {}
                for key, value in response.headers.items():
                    if key.lower() in headers:
                        headers[key.lower()] = f"{headers[key.lower()]}, {value}"
                    else:
                        headers[key.lower()] = value
                
                cookies: List[Dict[str, str]] = []
                for cookie in response.cookies.jar:
                    cookie_dict = {
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain or "",
                        "path": cookie.path or "/",
                    }
                    if cookie.expires:
                        cookie_dict["expires"] = str(cookie.expires)
                    cookies.append(cookie_dict)
                
                page_source = response.text
                
                return {
                    "headers": headers,
                    "cookies": cookies,
                    "page_source": page_source,
                }
            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching {url}: {str(e)}")
                raise Exception(f"HTTP error fetching {url}: {str(e)}")
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}", exc_info=True)
                raise Exception(f"Error fetching {url}: {str(e)}")


http_client = HTTPClient()

