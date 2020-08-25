# How to set up a local file system for Escalation
You need to have your data laid out as follows
- test_app_deploy_data/data/
   - <data_source_1_folder>
       - <data_source_1_file_1>.csv
       - <data_source_1_file_2>.csv
   - <data_source_2_folder>
       - <data_source_2_file_1>.csv
       - <data_source_2_file_2>.csv
       - <data_source_2_file_3>.csv
   - <data_source_3_folder>
       - <data_source_3_file_1>.csv  
       
All csv files in the same folder should have the same schema.
By default, it will use all the csv files in the folder.
This can be changed on the Admin tab on the webpage.  

## How to configure a graphic config file
- In the config file there is a key called "data_sources" which points to a dictionary with the following elements:
  - "main_data_source":{
    "data_source_type": <data_source>
}, -- this gives the first folder to find the data for this graphic.  
  - "additional_data_source" -- only needed if your graphic uses more than one data source
    - the second item in the list will look like. It points to a list of dictionaries where each element is  
     {
    "data_source_type": <another_data_source>,
"join_keys": \[
    \[
        <data_source from main_data_source>:<column_name>,
        <another_data_source>:<column_name>,
    \]}   

**All columns in the config file should be referenced as** <data_source_folder>:<column_name>
    