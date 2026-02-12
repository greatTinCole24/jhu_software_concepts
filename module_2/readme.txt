Name: ctindal3 | Cole Tindall

Module Info:
Module 2 - GradCafe Scraper + Cleaning
Due Date: 2/01/2026

Approach:
I implemented a GradCafe web scraper in "scrape.py" using "urllib3" for HTTP
requests and BeautifulSoup to parse the HTML table of results. The scraper
iterates through survey pages, extracts the schools listedd, program, date added, decision
status, and the detail row that contains GPA/GRE/citizenship/term ( this is where I got stuck) information.
I normalize whitespace with a small clean() helper and use regex to extract
numeric values (GPA, GRE, GRE V, GRE AW) ( stuck here also). The script writes the raw list of
entries to "raw_data.json".

For cleaning, "clean.py" loads the raw JSON and standardizes program and
university names to the best of my ability to mimic the llm.


Known Bugs:
Not able to get the llm_hosting to accurately clean the data 