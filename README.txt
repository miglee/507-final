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


------------the program is ran in the below environment------------
beautifulsoup4==4.6.0
bs4==0.0.1
certifi==2017.7.27.1
chardet==3.0.4
decorator==4.2.1
idna==2.6
ipython-genutils==0.2.0
jsonschema==2.6.0
jupyter-core==4.4.0
nbformat==4.4.0
nltk==3.2.5
oauthlib==2.0.6
plotly==2.4.0
PySocks==1.6.8
pytz==2018.3
requests==2.18.4
requests-oauthlib==0.8.0
selenium==3.11.0
six==1.11.0
traitlets==4.3.2
tweepy==3.6.0
urllib3==1.22
virtualenv==15.2.0

