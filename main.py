from bs4 import BeautifulSoup
import asyncio
import aiohttp

from dev import save_data


class WebScraper:
    def __init__(self, urls):
        self.urls = urls

    @staticmethod
    async def fetch_html(url, session):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            }

            async with session.get(url, timeout=60, headers=headers) as response:
                response.raise_for_status()  # Вызывает исключение для кода ответа 4xx/5xx
                return await response.text()
        except aiohttp.ClientError as e:
            print(f'Ошибка клиента: {e}')
            return None
        except asyncio.TimeoutError:
            print('Запрос превысил время ожидания')
            return None

    async def get_html_data(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = []

            for url in self.urls:
                tasks.append(self.fetch_html(url, session))

            results = await asyncio.gather(*tasks)
            return [result for result in results if result is not None]  # Удаляем None

class WebParser:
    async def parse_data(self, html_content):
        data = []
        for html in html_content:
            try:
                soup = BeautifulSoup(html, 'lxml')
                parsed_data = {
                    'title': soup.find(class_='tm-title tm-title_h1').text if soup.find(class_='tm-title tm-title_h1') else 'No Title',
                    'tags': [tag.text for tag in soup.find_all('a', class_='tm-tags-list__link')]
                }
                data.append(parsed_data)
            except Exception as e:
                print(f'Error: {e}')
        return data
class Pipeline:
    def __init__(self, urls):
        self.scraper = WebScraper(urls)
        self.parser = WebParser()
    async def run(self):
        print('Starting data pipeline...')

        scraped_data = await self.scraper.get_html_data()

        parsing = await self.parser.parse_data(scraped_data)

        save_data('parsed_pages.json', {'data': parsing})
        print(parsing)

        print('Pipeline completed!')

def main_menu():
    urls = []
    print('\nДобро пожаловать!')
    print('Введите ссылку на статью Хабра:')
    urls.append(input())
    while True:
        print('Добавить ещё одну ссылку?')
        print('1. Да')
        print('2. Нет, хватит')
        choice = input('Введите номер действия: ')
        if choice == '1':
            urls.append(input('Введите ссылку: '))
        elif choice == '2':
            return urls


if __name__ == "__main__":
    #['https://habr.com/ru/articles/870642/', 'https://habr.com/ru/articles/871426/']

    urls = main_menu()

    runner = Pipeline(urls)

    asyncio.run(runner.run())










