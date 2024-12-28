from bs4 import BeautifulSoup
import asyncio
import aiohttp

class WebScraper:
    def __init__(self, urls):
        self.urls = urls

    @staticmethod
    async def fetch_html(url, session):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            }

            async with session.get(url, timeout=20, headers=headers) as response:
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
    async def parse_data(self, html_content):
        try:
            soup = BeautifulSoup(html_content[0], 'lxml')
            parsed_data = {
                'title' : soup.find('meta', attrs={'name': 'title'})['content'],
                'tags' : [tag['content'] for tag in soup.find_all('a', class_='tm-tags-list__link')]
            }
            return parsed_data
        except Exception as e:
            print(f'Error: {e}')
            return {}

class Pipeline:
    def __init__(self, urls):
        self.scraper = WebScraper(urls)
        self.parser = WebParser()
    async def run(self):
        print('Starting data pipeline...')

        scraped_data = await self.scraper.get_html_data()

        parsing = await self.parser.parse_data(scraped_data)

        print(parsing)

        print('Pipeline completed!')

if __name__ == "__main__":
    urls = ['https://habr.com/ru/articles/870642/']

    runner = Pipeline(urls)

    asyncio.run(runner.run())










