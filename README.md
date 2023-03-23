# webz.io
webz.io crawler on turkhacks.com

in order to run the code please use Typer CLI from the **TurkHacks folder**

*Typer turkhacks.py run*

After runing the command you will find all the donloaded data under **./data** folder


#### NOTES-


Asomption and corner cuts that was made-

1. The crawler will continue to crawl the website even if the login process fails, allowing the crawler to gather as much data as possible.

2. Due to time constraints, a retry mechanism was not implemented. 

3. To ensure the crawler gathers as many posts as possible, the maximum timeout for the driver.set_page_load_timeout was set to 1 minute.

4. The thread identity is used as a prefix for each JSON file.

5. The website is protected by cloudflare, and to avoid detection, an undetected web driver was used.

6. Some of the wait times are greater than 3 seconds because it was found that 3 seconds was not always enough time to load the page.


