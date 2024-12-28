from bs4 import BeautifulSoup
import asyncio
import aiohttp

class WebScraper:
    def __init__(self, urls):
        self.urls = urls

    @staticmethod
    async def fetch_html(url, session):
        try:
            async with session.get(url, timeout=20) as response:
                response.raise_for_status()  # Вызывает исключение для кода ответа 4xx/5xx
                return await response.text()
        except aiohttp.ClientError as e:
            print(f'Ошибка клиента: {e}')
            return None
        except asyncio.TimeoutError:
            print('Запрос превысил время ожидания')
            return None

    async def get_html_data(self):
        async with aiohttp.ClientSession() as session:
            tasks = []

            for url in self.urls:
                tasks.append(self.fetch_html(url, session))

            return await asyncio.gather(*tasks)

class WebParser:
    def __init__(self, html_content):
        self.html_content = html_content




