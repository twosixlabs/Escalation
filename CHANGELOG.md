# 1.0.0

- Removes local csv handler option, tests, and documentation
- Adds script to reset database and models.py file to blank state.
- Numerical filters: 
    - only allow GTE/LTE instead of the wide range of operations, can set defaults for numerical filters
    - Non Numerical data is not allowed as a numerical filter
    - Only Numerical data with less than 200 unique entries is allowed as a filter
- Added graphical shape rendering to the layout schema (see https://plotly.com/javascript/shapes/)
- Adds httpbasicauth to admin endpoints, for very simple password protection of deployed app 
- Cookies and auth disabled in development mode, removing password protection and fixing bugs resulting from changing figures in development
- Additional testing, including basic browser functional testing and database functional tests
- Miscelaneous bug fixes


# 0.3.0

- Allows addition of error bars to plot so long as the error bar values are precalculated and contained in the data source.
- State of the dashboard is now saved as a cookie, so when one graph changes the rest do not.
- Cleans up plot toolbar and adds hide/show legend button
- Wizard modals are shown or hidden by default  based on context
- Improved data upload script using Flask API endpoint
- Adds app reset script for development/debugging