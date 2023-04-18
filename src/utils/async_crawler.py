import httpx
import asyncio
import html.parser
from typing import Callable, TypeAlias
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup

FilterFunc: TypeAlias = Callable[[str, str], str | None]

class UrlFilter:
    def __init__(
            self,
            allowed_domains: set[str] | None = None,
            allowed_schemes: set[str] | None = None,
            allowed_filetypes: set[str] | None = None,
    ):
        self.allowed_domains = allowed_domains
        self.allowed_schemes = allowed_schemes
        self.allowed_filetypes = allowed_filetypes

    def url_filter(self, base: str, url: str) -> str | None:
        url = urllib.parse.urljoin(base, url)
        url, *_ = urllib.parse.urldefrag(url)
        parsed = urllib.parse.urlparse(url)

        if (self.allowed_schemes is not None and parsed.scheme not in self.allowed_schemes):
            return None
        if (self.allowed_domains is not None and parsed.netloc not in self.allowed_domains):
            return None

        ext = Path(parsed.path).suffix
        if (self.allowed_filetypes is not None and ext not in self.allowed_filetypes):
            return None
        return url

class UrlParser(html.parser.HTMLParser):
    def __init__(self, base: str, url_filter: FilterFunc) -> None:
        super().__init__()
        self.base = base
        self.found_links = set()
        self.filter_func = url_filter

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        # find all links
        if tag != "a":
            return

        for attr, url in attrs:
            if attr != "href":
                continue

            url = self.filter_func(self.base, url)
            if url is not None:
                self.found_links.add(url)

class PasteParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.source_name: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "div":
            return

        for attr, value in attrs:
            if attr != "class":
                continue

            if value is not None:
                if 'source' in value:
                    self.source_name = value

class Crawler:
    def __init__(self, client: httpx.AsyncClient, starting_url: str, filter_func:FilterFunc, workers=10, limit=100, save_seen=False, load_seen=False) -> None:
        self.__client = client
        self.save_seen = save_seen
        self.load_seen = load_seen

        self.starting_url = starting_url
        self.seen = set()
        self.done = set()
        self.todo = asyncio.Queue()

        self.total = 0
        self.num_workers = workers
        self.limit = limit
        self.filter_func = filter_func

    async def run(self) -> None:
        # start by putting the starting url in the todo queue
        await self.todo.put(self.starting_url)

        if self.load_seen:
            try:
                with open("seen.txt") as f:
                    for url in f:
                        self.seen.add(url.strip())
            except FileNotFoundError:
                print("No seen.txt file found. Starting from scratch.")

        # create a list of workers
        workers = [asyncio.create_task(self.worker()) for _ in range(self.num_workers)]

        # wait for queue to be empty
        await self.todo.join()

        # free up resources
        for worker in workers:
            worker.cancel()

        if self.save_seen:
            # append seen urls to file
            with open("seen.txt", "a") as f:
                for url in self.seen:
                    f.write(url + "\n")

    async def worker(self) -> None:
        while True:
            url = await self.todo.get()
            try:
                await self.crawl(url)
            except Exception as e:
                print(f"Error crawling {url}: {e}")
            finally:
                self.todo.task_done()

    async def crawl(self, url: str) -> None:
        if url in self.done:
            return

        print(f"Crawling {url}")

        try:
            response = await self.__client.get(url, follow_redirects=True)
        except httpx.HTTPStatusError as e:
            print(f"Error getting {url}: {e}")
            return

        parser = PasteParser()
        parser.feed(response.text)

        if parser.source_name is not None:
            bs = BeautifulSoup(response.text, 'html.parser')
            contents = bs.find_all('div', attrs={'class': parser.source_name})

            path = Path(f"./code_snippets/{url.split('/')[-1]}.txt")
            print(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with path.open('w') as file:
                file.write(parser.source_name + '\n')
                for tag in contents:
                    file.write(tag.text.strip())

        urls = await self.parse_links(base=str(response.url), html=response.text)
        await self.update_links(urls)
        self.done.add(url)


    async def parse_links(self, base: str, html: str) -> set[str]:
        parser = UrlParser(base, self.filter_func)
        parser.feed(html)
        return parser.found_links

    async def update_links(self, urls: set[str]) -> None:
        new = urls - self.seen
        self.seen.update(new)

        for url in new:
            await self.push_todo_url(url)

    async def push_todo_url(self, url: str) -> None:
        if self.total >= self.limit:
            return
        self.total += 1

        await self.todo.put(url)


if __name__ == "__main__":
    url_filter = UrlFilter(
        allowed_domains={"pastebin.com"},
        allowed_schemes={"http", "https"},
        allowed_filetypes={".html", ".htm", ""},
    )

    async def main():
        async with httpx.AsyncClient() as client:
            crawler = Crawler(
                client,
                "https://www.pastebin.com/archive",
                url_filter.url_filter,
                workers=1,
                limit=5)
            await crawler.run()

    asyncio.run(main())