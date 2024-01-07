import pytest
import requests
from http import HTTPStatus

from imdb_movie_search.imdb import Imdb


class TestImdb:
    @pytest.fixture
    def mock_connection_error(self, monkeypatch):
        def _conn_error(*args, **kwargs):
            raise requests.exceptions.ConnectionError()

        monkeypatch.setattr(requests, "get", _conn_error)

    @pytest.fixture
    def mock_unexpected_error(self, monkeypatch):
        def _unexpected_error(*args, **kwargs):
            raise ValueError("unexpected error")

        monkeypatch.setattr(requests, "get", _unexpected_error)

    @pytest.fixture
    def mock_not_ok_response(self, monkeypatch):
        def _not_ok_response(*args, **kwargs):
            resp = requests.Response()
            resp.status_code = HTTPStatus.BAD_GATEWAY
            return resp

        monkeypatch.setattr(requests, "get", _not_ok_response)

    @pytest.fixture
    def single_movie_id(self):
        @staticmethod
        async def _single_movie_id(keyword, max_limit):
            return ["tt0201290"]

        return _single_movie_id

    @pytest.mark.asyncio
    async def test_movie_ids_request_connection_error(self, mock_connection_error):
        with pytest.raises(ConnectionError):
            await Imdb().search("comedy", 1)

    @pytest.mark.asyncio
    async def test_movie_ids_request_unexpected_error(self, mock_unexpected_error):
        with pytest.raises(ConnectionError):
            await Imdb().search("comedy", 1)

    @pytest.mark.asyncio
    async def test_movie_ids_request_not_ok(self, mock_not_ok_response):
        with pytest.raises(ConnectionRefusedError):
            await Imdb().search("comedy", 1)

    @pytest.mark.asyncio
    async def test_movie_ids_no_movie_section(self, monkeypatch):
        def _no_movie_section(*args, **kwargs):
            class MockResponse:
                def __init__(self) -> None:
                    self.status_code = HTTPStatus.OK
                    self.text = ""

            return MockResponse()

        monkeypatch.setattr(requests, "get", _no_movie_section)

        with pytest.raises(ValueError):
            await Imdb().search("comedy", 1)

    @pytest.mark.asyncio
    async def test_movie_ids_no_anchors(self, monkeypatch):
        def _no_anchors(*args, **kwargs):
            class MockResponse:
                def __init__(self) -> None:
                    self.status_code = HTTPStatus.OK
                    self.text = """<section data-testid="find-results-section-title"></section>"""

            return MockResponse()

        monkeypatch.setattr(requests, "get", _no_anchors)

        with pytest.raises(ValueError):
            await Imdb().search("comedy", 1)

    @pytest.mark.asyncio
    async def test_movie_ids_anchors_without_title_in_url(self, monkeypatch):
        def _anchor_without_title(*args, **kwargs):
            class MockResponse:
                def __init__(self) -> None:
                    self.status_code = HTTPStatus.OK
                    self.text = """<section data-testid="find-results-section-title"><a href="/abc"/></section>"""

            return MockResponse()

        monkeypatch.setattr(requests, "get", _anchor_without_title)

        await Imdb().search("comedy", 1) == []

    @pytest.mark.asyncio
    async def test_movie_ids_max_len_break(self, monkeypatch):
        def _anchor(*args, **kwargs):
            class MockResponse:
                def __init__(self) -> None:
                    self.status_code = HTTPStatus.OK
                    self.text = """<section data-testid="find-results-section-title"><a href="/title/tt0201290"/></section>"""

            return MockResponse()

        monkeypatch.setattr(requests, "get", _anchor)

        await Imdb().search("comedy", 0) == []

    @pytest.mark.asyncio
    async def test_movie_ids(self, monkeypatch):
        def _anchor(*args, **kwargs):
            class MockResponse:
                def __init__(self) -> None:
                    self.status_code = HTTPStatus.OK
                    self.text = """<section data-testid="find-results-section-title"><a href="/title/tt0201290"/></section>"""

            return MockResponse()

        @staticmethod
        async def _mock_movie_details(movie_id):
            return None

        monkeypatch.setattr(requests, "get", _anchor)
        monkeypatch.setattr(Imdb, "_extract_movie_detail", _mock_movie_details)
        await Imdb().search("comedy", 1) == []

    @pytest.mark.asyncio
    async def test_movie_detail_request_connection_error(
        self, monkeypatch, mock_connection_error, single_movie_id
    ):
        monkeypatch.setattr(Imdb, "_fetch_all_movie_ids", single_movie_id)
        with pytest.raises(ConnectionError):
            await Imdb().search("comedy", 1)

    @pytest.mark.asyncio
    async def test_movie_detail_request_unexpected_error(
        self, monkeypatch, mock_unexpected_error, single_movie_id
    ):
        monkeypatch.setattr(Imdb, "_fetch_all_movie_ids", single_movie_id)

        with pytest.raises(ConnectionError):
            await Imdb().search("comedy", 1)

    @pytest.mark.asyncio
    async def test_movie_detail_request_not_ok(
        self, monkeypatch, mock_not_ok_response, single_movie_id
    ):
        monkeypatch.setattr(Imdb, "_fetch_all_movie_ids", single_movie_id)

        with pytest.raises(ConnectionRefusedError):
            await Imdb().search("comedy", 1)

    @pytest.mark.asyncio
    async def test_movie_detail_no_section(self, monkeypatch, single_movie_id):
        monkeypatch.setattr(Imdb, "_fetch_all_movie_ids", single_movie_id)

        def _no_detail_section(*args, **kwargs):
            class MockResponse:
                def __init__(self) -> None:
                    self.status_code = HTTPStatus.OK
                    self.text = ""

            return MockResponse()

        monkeypatch.setattr(requests, "get", _no_detail_section)
        assert await Imdb().search("comedy", 1) == []

    @pytest.mark.asyncio
    async def test_movie_detail_unknown_value_for_section(
        self, monkeypatch, single_movie_id
    ):
        monkeypatch.setattr(Imdb, "_fetch_all_movie_ids", single_movie_id)

        def _invalid_detail_value(*args, **kwargs):
            class MockResponse:
                def __init__(self) -> None:
                    self.status_code = HTTPStatus.OK
                    self.text = """<script type="application/ld+json">abc</script>"""

            return MockResponse()

        monkeypatch.setattr(requests, "get", _invalid_detail_value)
        assert await Imdb().search("comedy", 1) == []

    @pytest.mark.asyncio
    async def test_success(self, monkeypatch, single_movie_id):
        monkeypatch.setattr(Imdb, "_fetch_all_movie_ids", single_movie_id)

        def _valid_detail_value(*args, **kwargs):
            class MockResponse:
                def __init__(self) -> None:
                    self.status_code = HTTPStatus.OK
                    self.text = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Movie","url":"https://www.imdb.com/title/tt0201290/","name":"The Underground Comedy Movie","image":"https://m.media-amazon.com/images/M/MV5BZmMyZTFhZTQtNzEyMS00MjIxLTg0YTAtYTQ1YTY3MjJmYmYxXkEyXkFqcGdeQXVyNjMwMjk0MTQ@._V1_.jpg","description":"A series of comedic short films guaranteed to offend.","review":{"@type":"Review","itemReviewed":{"@type":"Movie","url":"https://www.imdb.com/title/tt0201290/"},"author":{"@type":"Person","name":"planktonrules"},"dateCreated":"2010-02-16","inLanguage":"English","name":"Perhaps this should be the lowest rated film on IMDb, not the 91st worst--as 91st is way too kind.","reviewBody":"This film stars, among others, &quot;SlapChop&quot; Vince Offer (who also wrote, edited and directed) and Joey Buttafuoco--not exactly names that scream out &quot;quality&quot;. And with such uplifting skits as &quot;Supermodels taking a dump&quot; (it&apos;s exactly what it sounds like), a guy who robs a sperm bank (the &quot;Rhymer&quot;), necrophilia with a rotting corpse, black market fetuses (featuring a guy scooping what are supposed to be them out of a jar), lots and lots of gay jokes, a skit about a giant phallus who is a superhero and forced abortions. The skits are painfully unfunny (such as &quot;Batman and Rhymer&quot;), the acting not good enough to be considered amateurish and the film is crude just for the sake of being crude...and stupid. I truly believe a group of 8 year-olds could have EASILY made a funnier film with the same budget. Apparently this film resulted in a lawsuit by &quot;Slap Shot&quot; Vince against the Scientologists. Frankly, I wouldn&apos;t know who to root for in this case!!! Apparently, he alleged that somehow Scientologists destroyed his reputation and sank this film. No matter that the film is repellent junk from start to finish and 99% unfunny (by comparison, Ebola is funnier)...and these are the nicest things I can say about the movie. By the way, that IS Bobby Lee (from &quot;Mad TV&quot;) wearing a diaper and participating in the dumb fake porno film. It&apos;s amazing his career could overcome this.","reviewRating":{"@type":"Rating","worstRating":1,"bestRating":10,"ratingValue":1}},"aggregateRating":{"@type":"AggregateRating","ratingCount":2736,"bestRating":10,"worstRating":1,"ratingValue":1.9},"contentRating":"R","genre":["Comedy"],"datePublished":"1999-05-14","keywords":"crude humor,nipples,female frontal nudity,defecation,supermodel","actor":[{"@type":"Person","url":"https://www.imdb.com/name/nm0811069/","name":"Barbara Snellenburg"},{"@type":"Person","url":"https://www.imdb.com/name/nm0151612/","name":"Rebekah Chaney"},{"@type":"Person","url":"https://www.imdb.com/name/nm0818314/","name":"Gloria Sperling"}],"director":[{"@type":"Person","url":"https://www.imdb.com/name/nm0644399/","name":"Vince Offer"}],"creator":[{"@type":"Organization","url":"https://www.imdb.com/company/co0066280/"},{"@type":"Organization","url":"https://www.imdb.com/company/co0074988/"},{"@type":"Person","url":"https://www.imdb.com/name/nm0644399/","name":"Vince Offer"},{"@type":"Person","url":"https://www.imdb.com/name/nm1053523/","name":"Dante"}],"duration":"PT1H28M"}</script>'

            return MockResponse()

        monkeypatch.setattr(requests, "get", _valid_detail_value)
        res = await Imdb().search("comedy", 1)
        assert len(res) == 1
        assert res[0]["title"] == "The Underground Comedy Movie"
        assert res[0]["released_year"] == 1999
        assert res[0]["imdb_rating"] == 1.9
        assert res[0]["directors"] == ["Vince Offer"]
        assert res[0]["cast"] == [
            "Barbara Snellenburg",
            "Rebekah Chaney",
            "Gloria Sperling",
        ]
        assert (
            res[0]["plot_summary"]
            == "A series of comedic short films guaranteed to offend."
        )
