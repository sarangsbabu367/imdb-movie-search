# imdb-movie-search

A cli tool to search movies in imdb with keyword.

Objective: Create a Python web scraper that extracts movie information from IMDb. The scraper should be able to handle pagination and extract specific details about movies from multiple pages.

## Requirements:

Use IMDb's search functionality to search for a specific genre or keyword (e.g., "comedy" or "action"). Extract movie details from the search results.

Write a Python script that scrapes the following information for each movie:

* Title
* Release Year
* IMDb Rating
* Director(s)
* Cast
* Plot Summary
* Handle pagination.

If the search results span multiple pages, make sure your scraper can navigate through them and extract data from all pages.


Store the extracted data in a structured format like JSON or CSV.

Provide clear instructions on how to run the scraper and any dependencies it might have.

# Install

python is a prerequisite for this project, install python if not exists in the system.

Create and activate a virtual env.

> python3 -m venv env_imdb1

> source env_imdb1/bin/activate

Clone the project and move into project directory.

Install poetry

> pip install poetry

Install all dependencies

> poetry install

# How to use

Use `--help` argument to get more info about the tool.

```zsh
(env_imdb) ➜  imdb-movie-search git:(feat/movie-search) python imdb_movie_search/imdb.py --help
Usage: imdb.py [OPTIONS]

  This command will search the 'given keyword' in 'imdb' for movies and save
  the result in 'given file' (Maximum limit is 25).

Options:
  --k TEXT     Keyword to search for movies.  [required]
  --o TEXT     Outupt 'json' file path (movie_details.json,
               /Users/nick/downloads/movie_details.json).  [required]
  --d          To display the result in terminal.
  --m INTEGER  Maximum movie results which needs to be fetched (max limit is
               25).
  --help       Show this message and exit.
(env_imdb) ➜  imdb-movie-search git:(feat/movie-search)
```

## Example output

```zsh
(env_imdb) ➜  imdb-movie-search git:(feat/movie-search) python imdb_movie_search/imdb.py --d --k=comedy --o=movie_details.json --m=1                  
[{'cast': ['Robert De Niro', 'Jerry Lewis', 'Diahnne Abbott'],
  'directors': ['Martin Scorsese'],
  'imdb_rating': 7.8,
  'plot_summary': 'Rupert Pupkin is a passionate yet unsuccessful comic who '
                  'craves nothing more than to be in the spotlight and to '
                  'achieve this, he stalks and kidnaps his idol to take the '
                  'spotlight for himself.',
  'released_year': 1982,
  'title': 'The King of Comedy'}]
(env_imdb) ➜  imdb-movie-search git:(feat/movie-search) ✗ 
```

The same result is stored in given file name.

# Errors

Tool will throw errors in the below scenarios,

* Issue with connecting to imdb web page.
* Error response from imdb.
* If there are no movies with given 'keyword'.

## Example output

```zsh
(env_imdb) ➜  imdb-movie-search git:(feat/movie-search) ✗ python imdb_movie_search/imdb.py --d --k=fqwef --o=movie_details.json --m=1       
Traceback (most recent call last):
  File "/Users/sarang/work/imdb-movie-search/imdb_movie_search/imdb.py", line 176, in <module>
    asyncio.run(_main())
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/asyncclick/core.py", line 1157, in __call__
    return anyio.run(self._main, main, args, kwargs, **opts)
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/anyio/_core/_eventloop.py", line 73, in run
    return async_backend.run(func, args, {}, backend_options)
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/anyio/_backends/_asyncio.py", line 1991, in run
    return runner.run(wrapper())
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/anyio/_backends/_asyncio.py", line 193, in run
    return self._loop.run_until_complete(task)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/asyncio/base_events.py", line 642, in run_until_complete
    return future.result()
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/anyio/_backends/_asyncio.py", line 1979, in wrapper
    return await func(*args)
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/asyncclick/core.py", line 1160, in _main
    return await main(*args, **kwargs)
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/asyncclick/core.py", line 1076, in main
    rv = await self.invoke(ctx)
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/asyncclick/core.py", line 1434, in invoke
    return await ctx.invoke(self.callback, **ctx.params)
  File "/Users/sarang/work/imdb-movie-search/env_imdb/lib/python3.9/site-packages/asyncclick/core.py", line 780, in invoke
    rv = await rv
  File "/Users/sarang/work/imdb-movie-search/imdb_movie_search/imdb.py", line 165, in _main
    result: List[dict] = await Imdb().search(
  File "/Users/sarang/work/imdb-movie-search/imdb_movie_search/imdb.py", line 47, in search
    for movie_id in await self._fetch_all_movie_ids(keyword, max_limit):
  File "/Users/sarang/work/imdb-movie-search/imdb_movie_search/imdb.py", line 83, in _fetch_all_movie_ids
    raise ValueError(f"Unable to find any movies with keyword '{keyword}'")
ValueError: Unable to find any movies with keyword 'fqwef'
(env_imdb) ➜  imdb-movie-search git:(feat/movie-search) ✗ 
```

# Tests

Run tests with below command. `coverage` is added to dependency to display the coverage info of project.

```zsh
(env_imdb) ➜  imdb-movie-search git:(feat/movie-search) ✗ coverage run -m pytest tests/test_imdb.py && coverage report -m
====================================================== test session starts ======================================================
platform darwin -- Python 3.9.6, pytest-7.4.4, pluggy-1.3.0
rootdir: /Users/sarang/work/imdb-movie-search
plugins: asyncio-0.23.3, anyio-4.2.0
asyncio: mode=strict
collected 14 items                                                                                                              

tests/test_imdb.py ..............                                                                                         [100%]

====================================================== 14 passed in 0.18s =======================================================
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
imdb_movie_search/imdb.py      95      6    94%   165-172, 176
---------------------------------------------------------
TOTAL                          95      6    94%
(env_imdb) ➜  imdb-movie-search git:(feat/movie-search) ✗ 
```