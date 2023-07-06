import httpx
import asyncio
import html.parser
from typing import Callable, TypeAlias
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup

FilterFunc: TypeAlias = Callable[[str, str], str | None]

class UrlFilter:
    """
    A class used to filter URLs based on given parameters.

    Attributes
    ----------
    allowed_domains : set[str] | None
        A set of domains that are allowed.
    allowed_schemes : set[str] | None
        A set of URL schemes that are allowed.
    allowed_filetypes : set[str] | None
        A set of file extensions that are allowed.

    Methods
    -------
    url_filter(base: str, url: str) -> str | None:
        Applies the defined filters to a given URL and returns the URL if it passes all the filters.
    """
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
        """
        Applies the defined filters to a given URL.

        Parameters:
            base (str): The base URL to resolve against if the given URL is relative.
            url (str): The URL to filter.

        Returns:
            str | None: The URL if it passes all the filters; otherwise None.
        """
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
    """
    A class used to parse HTML and extract URLs.

    Attributes
    ----------
    base : str
        The base URL to resolve against if the extracted URLs are relative.
    found_links : set
        A set to store the extracted URLs.
    filter_func : FilterFunc
        A filter function to apply to the extracted URLs.

    Methods
    -------
    handle_starttag(tag: str, attrs: list[tuple[str, str]]) -> None:
        Extracts and filters URLs from the "href" attribute of "a" elements.
    """
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
    """
    A class used to parse HTML and extract code snippet sources.

    Attributes
    ----------
    source_name : str | None
        The name of the code snippet source.

    Methods
    -------
    handle_starttag(tag: str, attrs: list[tuple[str, str | None]]) -> None:
        Extracts the name of the code snippet source from the "class" attribute of "div" elements.
    """
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
    def __init__(self, client: httpx.AsyncClient, starting_url: str, filter_func:FilterFunc, workers=10, limit=100, rate_limiter: bool = False) -> None:
        """
        Initializes a Crawler with the given client, starting URL, filter function, number of workers, limit, and rate limiter.

        Parameters:
            client (httpx.AsyncClient): The HTTP client to use for making requests.
            starting_url (str): The URL to start crawling from.
            filter_func (FilterFunc): A filter function to apply to the extracted URLs.
            workers (int, optional): The number of workers to use for crawling. Defaults to 10.
            limit (int, optional): The maximum number of URLs to crawl. Defaults to 100.
            rate_limiter (bool, optional): Whether to limit the rate of requests. If true, sets the number of workers to 1 and the delay between requests to 1.5 seconds. Defaults to False.
        """
        self.__client = client

        self.starting_url = starting_url
        self.seen = set()
        self.done = set()
        self.todo = asyncio.Queue()

        self.total = 0
        self.num_workers = workers
        self.limit = limit
        self.filter_func = filter_func

        self.delay = 0
        if rate_limiter:
            self.num_workers = 1
            self.delay = 1.5

    async def run(self) -> None:
        """
        Starts the crawler with the given number of workers. Waits for the queue of URLs to be empty, then cancels the workers.
        """
        # start by putting the starting url in the todo queue
        await self.todo.put(self.starting_url)

        # create a list of workers
        workers = [asyncio.create_task(self.worker()) for _ in range(self.num_workers)]

        # wait for queue to be empty
        await self.todo.join()

        # free up resources
        for worker in workers:
            worker.cancel()

        print(f'crawled {len(self.done)} pages, {len(self.seen)} seen, {self.total} total')

    async def worker(self) -> None:
        """
        A worker that crawls URLs from the queue until it is empty. If an error occurs while crawling a URL, it prints the error and continues with the next URL.
        """
        while True:
            url = await self.todo.get()
            try:
                await self.crawl(url)
                await asyncio.sleep(self.delay)
            except Exception as e:
                print(f"Error crawling {url}: {e}")
            finally:
                self.todo.task_done()

    async def crawl(self, url: str) -> None:
        """
        Crawls a given URL, extracts new URLs from it, adds them to the queue, and stores the crawled URL. If an error occurs while getting the URL, it prints the error and returns.

        Parameters:
            url (str): The URL to crawl.
        """
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

            path = Path(f"./code_snippets/{url.split('/')[-1]}.{parser.source_name.split(' ')[-1]}.txt")
            path.parent.mkdir(parents=True, exist_ok=True)

            with path.open('w') as file:
                for tag in contents:
                    file.write(tag.text.strip())

        urls = await self.parse_links(base=str(response.url), html=response.text)
        await self.update_links(urls)
        self.done.add(url)


    async def parse_links(self, base: str, html: str) -> set[str]:
        """
        Parses HTML and extracts URLs from it.

        Parameters:
            base (str): The base URL to resolve against if the extracted URLs are relative.
            html (str): The HTML to parse.

        Returns:
            set[str]: The set of extracted URLs.
        """
        parser = UrlParser(base, self.filter_func)
        parser.feed(html)
        return parser.found_links

    async def update_links(self, urls: set[str]) -> None:
        """
        Updates the set of seen URLs with the given URLs and adds the new URLs to the queue.

        Parameters:
            urls (set[str]): The set of URLs to update with.
        """
        new = urls - self.seen
        self.seen.update(new)

        for url in new:
            await self.push_todo_url(url)

    async def push_todo_url(self, url: str) -> None:
        """
        Adds a URL to the queue of URLs to crawl, if the number of URLs added to the queue has not reached the limit.

        Parameters:
            url (str): The URL to add to the queue.
        """
        if self.limit != -1:
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
                workers=10,
                limit=500)
            await crawler.run()

    asyncio.run(main())