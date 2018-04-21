The program let you search for the most experienced hosts for a certain area on couchsurfing, 
save into database and provide interesting plotly graphs.

**The program uses SELENIUM to access data on webpages. 
**A chromedriver.exe under same directory as the python file is required to run the program.
**Users need to sign in to plotly with their own account in advance for the graphs to be generated successfully.
(https://plot.ly/)

The interaction prompt takes the following commands:

1. luckystar all/certain area(s) 
   (ex. luckystar all/ luckystar unitedstates):
   randomly provide a host from all or certain area(s)

2. number all/certain area(s) 
   (ex. number all/ number unitedstates,russia):
   show the chart of number of hosts from all or certain area(s)

3. gender all/certain area(s) 
   (ex. gender all/ gender chicago,sanfranscisco)
   show the chart of gender distribution of hosts from all or certain area(s)

4. age gender/area  all/certain area(s)
   (ex. age gender all/ age gender unitedstates/ age area all/ age area unitedstates,india)
   show the table of average age of genders/areas within all or certain area(s)

Others basic commands: exit, help
