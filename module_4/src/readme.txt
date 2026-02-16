Name: Cole Tindall ctindal3

Module Info:
Module 3 - GradCafe SQL + Flask Analysis
Due Date: 2/08/2026 11:59PM EST

Approach:
I set up a load of the cleaned GradCafe data from "module_2/applicant_data.json" ( this is sourced from teams doc) into a local
Postgres database using "load_data.py" script. loader defines single "applicants"
table with the required columns from the assignment(program, comments, date_added, url, status,
term, citizenship, GPA/GRE metrics, degree, and LLM-generated fields|| the loader parses dates into SQL DATE values and extracts numeric
values from strings like "GPA 3.95" or "GRE 320" using regex. ignores
duplicate URLs

For analysis, "query_data.py" runs assigned SQL queries against the "applicants"
table to answer the required questions. Queries filter by term (Fall
2026 etc...), status (Accepted/Rejected/Waitlistedd), degree type (Masters/PhD), and
program/university . 

web app "app.py" serves up a Flask page front end
with CSS styling (`static/styles.css`)(ai generated). page displays the query results and
two actions: a "Pull Data" button that runs the module 2 scrape.py + clean.py and reloads the database | "Update Analysis" button that refreshes
the results if no scrape is in progress. 

Known Bugs:
None known at this time.
