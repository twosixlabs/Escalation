# MVP Features
- Method not allowed; create another graph with same name as existing graph, create it on a page, get command doesn't work?
- If you rename the graph/page in the main config, can we rename the file rather than pointing to a new, empty file?
- data source affects what can be built
- and link to external Docker deployment instructions (Heroku? AWS free tier?)
- Don't just validate schema format, but run functional/integration test validation of data against required requests defined in config. Can we run all of the Handler functions against each dataset using the config file to make sure we have consistency between a config and a newly-uploaded data file?

# Nice to have Features

## graphics functionality
- Selecting other filters, when show all rows is selected by default, means you have to unselect show all rows or it overrides your selections
- Allow user to add their own hand-coded Plotly plots- where do they do the config, how is it included in the HTML?
- Save state of the website / user's preferences for graph configuration. Store the last form as a cookie and use it as the default? Store the form on the server side with a user-provided name and allow a user to select the form they want from a dropdown? This would work also as a way of sharing a graph config.
- Shareable graph configs- either a URL-encoded version for a GET that could be shared, or store a config server side that can be selected
- Nice to have: "decimation" feature- only plot a random sample of a big data set.

## Data management

- Using database/csv_to_sql.py with append doesn't work- upload_id needs to iterate
- Data privacy- do we want to add some kind of key checking or password functionality?
- Add data download option (both most recent data and older versions of the data?), with a url endpoint (on its own blueprint)
- Data upload options: 1) direct upload via a web interface 2) API upload which will interact with versioned data, etc. These methods probably use the same controller/model functionality, and the direct upload is just a web interface to the functionality.
- Time data file uploads via app endpoint. The app is still using pg8000. Should we switch to psycopg2 at the cost of more annoying local development? Or separate settings for local/deployed?
- Add data uploads table on app creation where we store active data and a history of uploads

## Wizard
- Validate Schema before uploading
- Combine wizard views into escalation app- we're running in debug mode, so it may work to just reboot the whole app on file changes. 
- Allow Tables in the wizard
- add pages in any order
- format/ validate form - use the dependencies
- add dependencies
- search for feature and where in the config it goes

## Testing
- Don't just validate schema format, but run functional/integration test validation of data against required requests defined in config. Can we run all of the Handler functions against each dataset using the config file to make sure we have consistency between a config and a newly-uploaded data file?
- Mock sql backend for testing
- Test file upload

# USER STORIES

Real time data from fermenter (temp, pH) with updates on dashboard, including
