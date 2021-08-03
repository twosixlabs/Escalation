# Copyright [2021] [Two Six Technologies, LLC]
# Licensed under the Apache License, Version 2.0
import pandas

"""
In general Escalation has been built assuming that you're uploading files that are more or less ready for visualization.
However, in some cases there are simple transforms that we'd like to apply to an uploaded file that can't easily be done in the visualization at runtime.
If for a type of files there are functions that you'd like to run, the should be defined below.
"""


# define transform functions included in FILE_UPLOAD_FUNCTION_MAPPING below.
# functions should take as argument and return a single pandas dataframe
# def function_template(datafile: pandas.DataFrame) -> pandas.DataFrame:
    # datafile['new_column'] = datafile['old_column'] / 3.14
    # return datafile

def function_template(datafile: pandas.DataFrame) -> pandas.DataFrame:
    return datafile


FILE_UPLOAD_FUNCTION_MAPPING = {
    # list functions here in key:value form "data_source_name": [function1, function2]
    # where data_source_name is the name defined for an upload in the file upload page ("Data File Type", which matches the table name in sql)
    # and where the list in the value is the functions to be applied, in order
}
