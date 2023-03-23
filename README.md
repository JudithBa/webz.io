# webz.io
webz.io crawler on turkhacks.com

in order to run the code please use Typer CLI from the turkhacks folder

Typer turkhacks.py run


NOTES-


Asomption and corner cuts that was made-

1. The crawler continue to crawl the website even if the login failed
2. Due to time constraints, the implementation of a retry mechanism was not done.
3. I assumed that the main goal is to get as many posts as possible so that's why driver.set_page_load_timeout set to 1 min max.
4. each json file have the thread identity as a prefix
5. the website have cloudflare anti-bot protection so i use undetected web driver
6. some of the wait are greater then 3 sec because 3 sec wasn't enough wait to load the page


