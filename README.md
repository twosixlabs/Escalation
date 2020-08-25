# Escalation

## What is Escalation?
Escalation is a web app that runs a lightweight visualization dashboard for data analysis. 
You can set up plots and tables that update along with your data or analysis, and have interactivity options to allow for data browsing.

Some user cases for Escalation:
- A research group that wants to have better visibility into experiments conducted by its members, or an at-a-glance record of experimental progress
- A project team at a small company that wants to share progress or up to date results with management

All that is required for is to set a config file, either by hand or using the included UI Configuration Wizard, 
and you can run Escalation locally or on a server for others to view.

You can see an example of Escalation running on data for DARPA's Synergistic Discovery and Design program [here](http://escos.sd2e.org/). We also have a demo app (ToDo: Include link to Penguin demo app instructions)


## Wait, aren't there already lots of different visualization tools out there?
Yes. Escalation has a few advantages:
- Straightforward and low-cost deployment
- Improved data privacy: everything can be hosted and run locally or on a server you control
- Open-source code
- Integration with data versioning and analysis pipelines (In development)


## What are the limitations of Escalation?
As of the current version:
* Plots only a single line or scatter plot.
* Need to be connected to the internet
* Use a SQL database or local csv files (assuming csv in local handler)
* Local handler currently gets most recent data set

# Setup

## What do you need for the app to work?

- [Configuration files](#Building-Configuration-files)
    - Escalation uses configuration files (json) to build the dashboard organizational structure, link the data in visualizations, and construct the visualizations themselves.
    - These configuration files can be built by hand, using the Configuration Wizard, or any combination of the two
- [Data](#Loading-your-data) 
    - When setting up Escalation, you choose to use either a CSV or SQL backend.
    - Depending on the backend, you'll either link the app to a database (new or existing) or a file system path containing your data files. 
     A file backend may be easier for those unfamiliar with SQL, but SQL is more performant, and storing data in a database offers advantages beyond the database's use in Escalation
    - Escalation includes tooling to ingest CSV files into SQL, automatically building the necessary SQL data tables and the code necessary to integrate them with Escalation.
    - ToDo: Data Migration helpers- what happens when the format of your data changes over time?
- [Python environment to run the app](#Running-the-app)
    - You need a Python environment set up to run the web app. See instructions for setting up an environment, using Docker to handle the environment for you.

Each of these components are discussed further below.

## 1. Stand up empty instances of the web app and database using Docker

From the root level of the code repository, run: 

`docker-compose build`

(this takes a little while the first time, as components are downloaded and installed)

We recognize that Docker is less common in academic settings, but highly recommend using it. 
Here are [instructions](https://docs.docker.com/get-started/) on getting started using Docker.
We use the Docker containers to run our configuration wizard, as well as the scripts to ingest csv data into a SQL database.
Once we set up a configuration and your data, we'll also use these containers to run the web app.

## 2. Load your data

### SQL database backend
    
We provide a script to parse csv data files, determine the relevant sql schema, and create tables in the SQL database from your file. 
The script uses the infrastructure of the Docker containers you built, so there is no need to install anything else.

Run the script from the top level directory of the repo

    ./escalation/csv_to_sql.sh {name_of_sql_table} {ABSOLUTE path_to_csv_file} {replace/append/fail}
    
example usage: 

    ./escalation/csv_to_sql.sh experimental_stability_score /Users/nick.leiby/repos/versioned-datasets/data/protein-design/experimental_stability_scores/100K_winter19.v1.experimental_stability_scores.csv replace

This creates sql tables that can be used by the graphics and tables on your Escalation dashboard.

Run this script for each file you'd like to use for your visualizations and include in the database. Note, it may take a little while to run.

The flag replace, append, or fail is instructions for what to do if a sql table of that name already exists,
 as per the [pandas](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html) method used for ingestion.

If you'd like to add more than one csv to the same table, you have two options: combine them before running the script, or wait until the Escalation web app is running, and submit the additional CSVs as new data to the app (explained below, Todo: Here)
Todo: If you have an existing SQL database, how do you copy it into Escalation?
Todo: On the feature roadmap- add csvs using the web interface rather than a shell script

### CSV data file system backend

How to set up a [local file system backed](config_information/local_example/local_data_storage_config_info.md) Escalation app.  
    
## 3. Building Configuration files

### Use the Configuration Wizard

Run the configuration wizard app from the root directory of this repo:
    
    ./escalation/wizard_ui/wizard_launcher.sh
    
This launches the Configurer UI Wizard in a Docker container. Navigate in your the web app in your browser at: [http://localhost:8001](http://localhost:8001) or [http://127.0.0.1:8001](http://127.0.0.1:8001)
   
To see how your config looks in Escalation, launch the web app in debug mode: 

    ./escalation/wizard_ui/web_app_debug_launcher.sh

Navigate to the Escalation app in your browser at: [http://localhost:8000](http://localhost:8000) or [http://127.0.0.1:8000](http://127.0.0.1:8000). 
This app runs in debug mode, and should detect the changes you make as you edit the configuration. 
Refresh your browser to update the contents to match your saved configuration.
     
Some notes on [creating your first config files with the UI wizard](config_information/wizard_guide/creating_first_graphic_with_wizard.md).  


### Build a config from scratch (advanced)
Run `python build_app_config_json_template.py` to build a base config file. 
Everything blank or in `<>` should be changed.

### Debugging config files manually (advanced)

How to set up [local file system and config](config_information/local_example/local_data_storage_config_info.md) for the app.  
An example of a [main config file](config_information/main_config_example/main_config_example.md).  
Examples of [different plots and graphic config files](config_information/plotly_examples/plotly_config_info.md).  
Examples of [different selectors](config_information/selector_examples/selector_config_info.md). 

## Running the app

We recommend running the Escalation web app using the docker container:

Re-run the docker compose build command to re-launch the containers with the app including all of the configuration you just did:

    docker-compose up --build -d
    
To use the app, navigate in your browser to: [http://localhost:8000](http://localhost:8000) or [http://127.0.0.1:8000](http://127.0.0.1:8000)

## connecting directly to the SQL database 

    docker exec -it escos_db psql -h localhost -p 5432 -U escalation -d escalation

## Resetting the SQL database

Todo: deleting the db volume

Todo: running docker cleanup

# Running Escalation as a web-accessible server


In summary, you'll build a Docker-compose image that includes your dashboard configuration, and deploy it on a web-accessible server. 
This can be a server on a local network, e.g. in your lab, or on a cloud provider like [DigitalOcean](https://www.digitalocean.com/docs/droplets/quickstart/), Heroku, or AWS.

## Building your Docker image for deployment

1. You'll want to change the default settings for the password and username for the database, defined here: `escos/escalation/app_deploy_data/app_settings.py`
2. 

# How can I contribute? (advanced)

### Running Locally, without using Docker (useful for Escalation code development, testing)

You can also set up a custom Python virtual environment and run the server locally as you would any other Flask web app. 
ToDo: More detailed instructions on virtual env setup, requirements install,  and running the app. Include info about db connection from host to Docker db

### Developing for Escalation

- `pip install -r requirements-dev.txt`
- `pre-commit install` sets up the pre-commit hooks to auto-format the code. This is optional, the repo is formatted with Flake and Black. 


### How to add a new type of plot
Development for Escalation has focused on Plotly, but the codebase should be compatible with other libraries or custom graphics. If you want to use something other than Plotly, your code should:
* Needs to inherit from graphic_class.py
* Be added to available_graphics.py
* Include an html file with javascript code required to plot

### How to add a new option feature
* add it to available_selectors.py
* create a html document input elements need name "\<id>|\<type>|<column_name>"
* add to create_data_subselect_info and reformat_filter_form_dict in controller.py
* build in functionality graphics_class or data_storer class
 

# License

The Apache 2.0 License applies to all code and materials associated with Escalation.


Copyright \[2020] \[Two Six Labs, LLC]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

