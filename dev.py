import json

from bs4 import BeautifulSoup
import asyncio
import aiohttp


async def save_data(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def main_menu(parsed_data):
    print('\nДобро пожаловать!')
    word = input('Введите ключевое слово: ')
    articles = [article for article in parsed_data if word in article['title']]
    return articles


class WebScraper:
    def __init__(self, urls):
        self.url = urls

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

            url_part = self.url

            # Здесь я немного наговнокодил, потому что сервер перегружался из-за количества запросов и выдавал ошибки
            # кодом ниже я получаю не сразу все 50 страниц параллельно, а по частям
            # Можно это ещё и в функцию так-то обернуть и уменьшить кол-во кода, но пофиг
            for page_number in range(1, 21):
                url_path = f'{url_part}{page_number}'
                tasks.append(self.fetch_html(url_path, session))

            results = await asyncio.gather(*tasks)
            results = [result for result in results if result is not None]

            tasks2 = []

            url_part = self.url

            for page_number in range(21, 41):
                url_path = f'{url_part}{page_number}'
                tasks2.append(self.fetch_html(url_path, session))

            results2 = await asyncio.gather(*tasks2)

            for res in results2:
                if res is not None:
                    results.append(res)

            tasks3 = []

            url_part = self.url

            for page_number in range(41, 51):
                url_path = f'{url_part}{page_number}'
                tasks3.append(self.fetch_html(url_path, session))

            results3 = await asyncio.gather(*tasks3)

            for res in results3:
                if res is not None:
                    results.append(res)

            return results


class WebParser:
    @staticmethod
    async def parse_data(html_content):
        data = []
        for html in html_content:
            try:
                soup = BeautifulSoup(html, 'lxml')

                for title in soup.find_all(class_='tm-title__link'):
                    data.append({'title': title.text,
                                 'href': f'https://habr.com{title.get('href')}'
                                 })
            except Exception as e:
                print(f'Error: {e}')
        print(f'Импортировано статей: {len(data)}')
        return data


class Pipeline:
    def __init__(self, urls):
        self.scraper = WebScraper(urls)
        self.parser = WebParser()

    async def run(self):
        print('Starting data pipeline...')

        scraped_data = await self.scraper.get_html_data()

        parsed_data = await self.parser.parse_data(scraped_data)

        final_data = main_menu(parsed_data)

        asyncio.run(save_data('parsed_articles.json', {'data': final_data}))

        print('Вот необходимые статьи: ', final_data)

        print('Pipeline completed!')


if __name__ == "__main__":
    url1 = f'https://habr.com/ru/articles/top/alltime/page'

    runner = Pipeline(url1)

    asyncio.run(runner.run())
