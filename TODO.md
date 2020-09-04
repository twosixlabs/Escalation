# Next release todo Features
- Ability to rename pages
- Selecting other filters, when show all rows is selected by default, means you have to unselect show all rows or it overrides your selections

# Nice to have Features

## graphics functionality
- Allow user to add their own hand-coded Plotly plots- where do they do the config, how is it included in the HTML?
- Save state of the website / user's preferences for graph configuration. Store the last form as a cookie and use it as the default? Store the form on the server side with a user-provided name and allow a user to select the form they want from a dropdown? This would work also as a way of sharing a graph config.
- Shareable graph configs- either a URL-encoded version for a GET that could be shared, or store a config server side that can be selected
- Nice to have: "decimation" feature- only plot a random sample of a big data set.
- rich hover text- images? HTML?

## Data management

- Data privacy- do we want to add some kind of key checking or password functionality?
- Add data download option (both most recent data and older versions of the data?), next to identifiers on admin page
- script to update models.py. Integrate with delete db to clear db but leave metadata
- Render validation error response on file upload in HTML rather than printing json

## Wizard
- Allow Tables in the wizard
- add pages in any order
- search for feature (opacity, hover text) and where in the config it goes
- in-line documentation to configuration wizard-Add a second column to the config wizard that explains the properties that can be edited in a specific dropdown? Lots of hover text?
- reloading the editor after a post generates the same post effects again- duplicating the new additions

## Testing
- Don't just validate schema format, but run functional/integration test validation of data against required requests defined in config. Can we run all of the Handler functions against each dataset using the config file to make sure we have consistency between a config and a newly-uploaded data file?
- Test file upload

## Deployment
- How much RAM do we need to handle big data files? Can we stream things more efficiently than Pandas is doing?
- add link to external Docker deployment instructions (Heroku? AWS free tier? Google Cloud Run?)


# USER STORIES

Real time data from fermenter (temp, pH) with updates on dashboard, including
Data-enabled publication. Upload static set of data and interactive viz to accompany a paper
