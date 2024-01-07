"""Imdb web scrapper."""
from typing import Final, List, Optional
import requests
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, asdict
from http import HTTPStatus
import ast
import asyncclick as click
import json
from pprint import pprint
import asyncio


_MAX_MOVIE_COUNT: Final = 25
_MOVIE_LIST_URL: str = "https://www.imdb.com/find?q={keyword}&ttype=ft&s=tt"
_MOVIE_DETAILS_URL: str = "https://www.imdb.com/title/{id}"
_IMDB_HEADERS: Final = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    "Referer": "https://www.imdb.com/",
}


@dataclass(frozen=True)
class _MovieInfo:
    """Details about a movie."""

    title: str
    released_year: Optional[int]
    imdb_rating: Optional[float]
    directors: List[str]
    cast: List[str]
    plot_summary: Optional[str]


class Imdb:
    """Scrapper which parse imdb information."""

    def __init__(self) -> None:
        pass

    async def search(self, keyword: str, max_limit: int) -> List[dict]:
        """Search imdb with given keyword for movies.
        max limit is set as 25 to avoid throttling from imdb.
        """
        movie_details: List[_MovieInfo] = []
        for movie_id in await self._fetch_all_movie_ids(keyword, max_limit):
            if (movie_info := await self._extract_movie_detail(movie_id)) is not None:
                movie_details.append(asdict(movie_info))
        return movie_details

    @staticmethod
    async def _fetch_all_movie_ids(keyword: str, max_limit: int) -> List[str]:
        """Get all movie ids from the search result in imdb.

        note: keep the movie ids under max limit.
        """
        try:
            response = requests.get(
                _MOVIE_LIST_URL.format(keyword=keyword), headers=_IMDB_HEADERS
            )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Unable to connect. Please check your internet connection."
            )
        except Exception:
            raise ConnectionError("Unable to fetch details. Try again after sometimes.")

        if response.status_code != HTTPStatus.OK:
            raise ConnectionRefusedError(
                f"imdb responded with status '{response.status_code}'"
            )

        soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
        movie_section: Optional[Tag] = soup.find(
            "section", attrs={"data-testid": "find-results-section-title"}
        )
        if not movie_section:
            raise ValueError(f"Unable to find any movies with keyword '{keyword}'")

        anchors: List[Tag] = movie_section.find_all("a")
        if not anchors:
            raise ValueError(f"Unable to find any movies with keyword '{keyword}'")

        movie_ids: List[str] = []
        for anchor in movie_section.find_all("a"):
            if "/title" not in anchor["href"]:
                continue
            if len(movie_ids) == max_limit:
                break
            # "/title/tt0201290/?ref_=fn_tt_tt_11" -> "tt0201290"
            movie_ids.append(
                anchor["href"].split("?", 1)[0].strip("/").split("/", 1)[1]
            )
        return movie_ids

    @staticmethod
    async def _extract_movie_detail(movie_id: str) -> Optional[_MovieInfo]:
        """Extract the required details about the movie from imdb."""
        try:
            response = requests.get(
                _MOVIE_DETAILS_URL.format(id=movie_id), headers=_IMDB_HEADERS
            )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Unable to connect. Please check your internet connection."
            )
        except Exception:
            raise ConnectionError("Unable to fetch details. Try again after sometimes.")

        if response.status_code != HTTPStatus.OK:
            raise ConnectionRefusedError(
                f"imdb responded with status '{response.status_code}'"
            )

        soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
        movie_details_tag: Optional[Tag] = soup.find(
            "script", attrs={"type": "application/ld+json"}
        )
        if not movie_details_tag:
            return None
        try:
            movie_details: dict = ast.literal_eval(movie_details_tag.text)
        # Some invalid format.
        except ValueError:
            return None
        released_year, plot_summary, imdb_rating = None, None, None
        if "datePublished" in movie_details:
            released_year = int(movie_details["datePublished"].split("-", 1)[0])
        if "aggregateRating" in movie_details:
            imdb_rating = movie_details["aggregateRating"].get("ratingValue")
        if "description" in movie_details:
            plot_summary = movie_details["description"]
        return _MovieInfo(
            title=movie_details["name"],
            released_year=released_year,
            imdb_rating=imdb_rating,
            directors=[
                director_node["name"] for director_node in movie_details["director"]
            ],
            cast=[cast_node["name"] for cast_node in movie_details["actor"]],
            plot_summary=plot_summary,
        )


@click.command()
@click.option("--k", required=True, help="Keyword to search for movies.")
@click.option(
    "--o",
    required=True,
    help="Outupt 'json' file path (movie_details.json, /Users/nick/downloads/movie_details.json).",
)
@click.option(
    "--d", is_flag=True, default=False, help="To display the result in terminal."
)
@click.option(
    "--m",
    default=_MAX_MOVIE_COUNT,
    help="Maximum movie results which needs to be fetched (max limit is 25).",
)
async def _main(k: str, o: str, d: bool, m: int):
    """This command will search the 'given keyword' in 'imdb' for movies
    and save the result in 'given file' (Maximum limit is 25).
    """
    result: List[dict] = await Imdb().search(
        k, m if 1 <= m <= _MAX_MOVIE_COUNT else _MAX_MOVIE_COUNT
    )
    if d is True:
        pprint(result)

    with open(o, "w") as dest:
        json.dump(result, dest)


if __name__ == "__main__":
    asyncio.run(_main())
