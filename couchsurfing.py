import codecs
import sys
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup
import sqlite3
import plotly
# plotly.tools.set_credentials_file(username='xxxxx', api_key='xxxxx')
import plotly.plotly as py
import plotly.graph_objs as go
from random import randint


#set cache file name
CACHE_FNAME = "cache.json"
DBNAME = "Couchsurfing.sqlite3"

#get cache dict from cache file or create an empty cache dict
try:
    f = open(CACHE_FNAME,'r')
    rf = f.read()
    CACHEDICT = json.loads(rf)
    f.close()
except:
    CACHEDICT = {}

#unique request formatting
#unique_request
def params_unique_combination(baseurl, params_d={}, private_keys=["api_key",'api-key']):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

#parser settings
class Parser:
    def __init__(self):
        
        self._options = webdriver.ChromeOptions()
        self._options.add_argument("window-size=1200x600")
        self._options.add_argument("--disable-notifications")
        self._driver = webdriver.Chrome(executable_path=r'chromedriver.exe', chrome_options=self._options)
        
        # set implicitly wait time
        self._timeout = 10
        self._driver.implicitly_wait(self._timeout)

        # initialise cookie
        self._cookies = {}

        # initialise all profile_pages
        self._profile_pages = []

        # set retries
        self._retries = 5


#get number of results and userlinks html of hosts of a given area 
#(use "find elements" to grab certain blocks of html instead of the whole page to avoid javascript data loading issue)
    def get_resultnumber_userlinks(self,area,page=5):
        url="https://www.couchsurfing.com/members/hosts?utf8=%E2%9C%93&search_type=host&search_query="+area+"&host_sort=1"
        uniquerequest = params_unique_combination(url, {"type":"partial_html"})

#get cached data if any
        if uniquerequest in CACHEDICT:
            print("collect cached data")
            resultnumberhtml = CACHEDICT[uniquerequest]['resultnumberhtml']
            userscardshtml = CACHEDICT[uniquerequest]['userscardshtml']

#request and get html elements if there's no cache data
        else:
            print("get new data")
            self._driver.get(url)
            resultnumberhtml = []
            userscardshtml = []
            pagenumber = 1
            resultnumberelement = self._driver.find_elements_by_xpath('//*[@class="text mod-gray mod-normal mod-tight u-left js-search-results-count"]')
            for a in resultnumberelement:
                resultnumberhtml.append(a.get_attribute('outerHTML'))

            userscardselement = self._driver.find_elements_by_xpath('//*[@class="user-card"]')
            for elem in userscardselement:
                userscardshtml.append(elem.get_attribute('outerHTML'))

#go to next page and get user links html
            while pagenumber < page:
                button = self._driver.find_element_by_xpath('//button[@title="Next Page"]')
                button.click()
                pagenumber+=1
                
                userscardselement = self._driver.find_elements_by_xpath('//*[@class="user-card"]')
                for elem in userscardselement:
                    userscardshtml.append(elem.get_attribute('outerHTML'))
                print("get data from "+str(pagenumber)+" pages, found " +str(len(userscardshtml))+" users.")

#put new data to cache dict and save to cache file
                CACHEDICT[uniquerequest] = {}
                CACHEDICT[uniquerequest]['resultnumberhtml'] = resultnumberhtml
                CACHEDICT[uniquerequest]['userscardshtml'] = userscardshtml

                outfile = open(CACHE_FNAME,'w',encoding='UTF-8')
                outfile.write(json.dumps(CACHEDICT))
                outfile.close()
    
# extract result number and userlinks from html
        userslinks = []

        for a in resultnumberhtml:
            soup = BeautifulSoup(a,'html.parser')
            resultnumber = soup.find('h2')['data-count']
        for a in userscardshtml:
            soup = BeautifulSoup(a,'html.parser')
            userslinks.append("https://www.couchsurfing.com"+soup.find('a')['href'])


        return resultnumber,userslinks

# get user info from a given userlink
    def get_user_info(self,userlink):
        uniquerequest = params_unique_combination(userlink, {"type":"partial_html"})

#get data from cache dict if any
        if uniquerequest in CACHEDICT:
            print("collect cached data")
            part1element = CACHEDICT[uniquerequest]['part1element']
            part2element = CACHEDICT[uniquerequest]['part2element']

        else:
            print("get new data")
            self._driver.get(userlink)
            part1element = self._driver.find_elements_by_xpath('//span[contains(@class, "profile-sidebar__username-link text")]')
            part2element = self._driver.find_elements_by_xpath('//ul[@class="mod-icon-bullets"]')
            part1element = part1element[0].get_attribute('outerHTML')
            part2element = part2element[0].get_attribute('outerHTML')


#put new data into cache dict and save cache dict to cache file 
            CACHEDICT[uniquerequest] = {}
            CACHEDICT[uniquerequest]['part1element'] = part1element     
            CACHEDICT[uniquerequest]['part2element'] = part2element
    
            outfile = open(CACHE_FNAME,'w')
            outfile.write(json.dumps(CACHEDICT))
            outfile.close()

#extract user info from html

        soup = BeautifulSoup(part1element,'html.parser')
        try:
            name = soup.text
        except:
            name = "N/A"
        soup = BeautifulSoup(part2element,'html.parser')
        if "Ambassador" in soup.text:
            listindex = 3
        else:
            listindex = 2
        lists = soup.find_all('li')
        try:
            age = lists[listindex].text.split(',')[0].strip()
        except:
            age = None
        try:
            gender = lists[listindex].text.split(',')[1].strip()
        except:
            gender = "N/A"
        try:
            signuptime = lists[listindex+1].text.split()[2].strip()
        except:
            signuptime = None
        return [name, userlink, age, gender, signuptime]

#create db tables
def create_db_tables():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
            DROP TABLE IF EXISTS 'Areas';
        '''
    cur.execute(statement)

    statement = '''
            DROP TABLE IF EXISTS 'Users';
        '''
    cur.execute(statement)

    statement = "CREATE TABLE 'Areas' ( "
    statement +="'Id' integer Primary key autoincrement, "
    statement +="'AreaName' text, "
    statement +="'ResultNumber' integer "
    statement +=")"
    cur.execute(statement)


    statement = "CREATE TABLE 'Users' ( "
    statement +="'Id' integer Primary key autoincrement, "
    statement +="'Name' text, "
    statement +="'UserLink' text, "
    statement +="'Area' text, "
    statement +="'Age' integer, "
    statement +="'Gender' text, "
    statement +="'SignUpTime' integer,foreign key(Area) references Areas(AreaName) "
    statement +=")"
    cur.execute(statement)

    conn.commit()
    conn.close()

#insert python object data into db
def insert_pyobject_data_into_db(area, resultnumber, usersinfolist):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "INSERT INTO Areas "
    statement +="Values ("
    statement +="NULL,?,? "
    statement +=")"
    insertion = (area,resultnumber)
    cur.execute(statement,insertion)
    conn.commit()

    for user in usersinfolist:
        statement = "INSERT INTO Users "
        statement +="Values ("
        statement +="NULL,?,?,?,?,?,? "
        statement +=")"
        insertion = (user[0],user[1],area,user[2],user[3],user[4])

        cur.execute(statement, insertion)

    conn.commit()
    conn.close()


#class of hosts
class Host():
    def __init__(self,userinfo):
        self.name = userinfo['name']
        self.link = userinfo['userlink']
        self.area = userinfo['area']
        self.age = userinfo['age']
        self.gender = userinfo['gender']
        self.signuptime = userinfo['signuptime']
    def __str__(self):
        exprience = 2018-self.signuptime
        return "{}, {} host in {}, {} years old. Has been in Couchsurfing for {} years.".format(self.name,self.gender, self.area,self.age, exprience)

# make number chart

def make_number_chart(areas,resultnumbers):

    data = [go.Bar(
            x=areas,
            y=resultnumbers,
            )]

    py.plot(data, filename='number of hosts in given areas',world_readable=True)


def make_gender_chart(titles,maleportion,femaleportion):

    male = {"x":titles,"y":maleportion,"marker": {"color": "rgb(253, 218, 0)"},"name": "male", "type": "bar"}
    female = {"x":titles,"y":femaleportion,"marker": {"color": "rgb(253, 260, 0)"},"name": "female", "type": "bar"}


    data = [male, female]
    layout = {

      "annotations": [
        {
          "x": 0.1, 
          "y": 0.3, 
          "align": "center", 
          "arrowcolor": "rgba(68, 68, 68, 0)", 
          "arrowhead": 1, 
          "arrowsize": 1, 
          "arrowwidth": 0, 
          "ax": 1, 
          "ay": 255.608329773, 
          "bgcolor": "rgba(0,0,0,0)", 
          "bordercolor": "", 
          "borderpad": 1, 
          "borderwidth": 1, 
          "font": {
            "color": "", 
            "family": "", 
            "size": 0
          }, 
          "opacity": 1, 
          "showarrow": True, 
          "text": "Data: couchsurfing.com", 
          "xanchor": "auto", 
          "xref": "paper", 
          "yanchor": "auto", 
          "yref": "paper"
        }
      ], 
      "autosize": False, 
      "bargap": 0.2, 
      "bargroupgap": 0, 
      "barmode": "stack", 
      "boxgap": 0.3, 
      "boxgroupgap": 0.3, 
      "boxmode": "overlay", 
      "dragmode": "zoom", 
      "font": {
        "color": "#444", 
        "family": "Raleway, sans-serif", 
        "size": 12
      }, 
      "height": 800, 
      "hidesources": True, 
      "hovermode": "x", 
      "legend": {
        "x": 1.01889808481, 
        "y": 0.958064516129, 
        "bgcolor": "rgba(255, 255, 255, 0)", 
        "bordercolor": "#444", 
        "borderwidth": 0, 
        "font": {
          "color": "", 
          "family": "", 
          "size": 0
        }, 
        "traceorder": "reversed", 
        "xanchor": "left", 
        "yanchor": "top"
      }, 
      "margin": {
        "r": 80, 
        "t": 100, 
        "autoexpand": True, 
        "b": 80, 
        "l": 80, 
        "pad": 0
      }, 
      "paper_bgcolor": "rgb(255, 255, 255)", 
      "plot_bgcolor": "#fff", 
      "separators": ".,", 
      "showlegend": True, 
      "title": "<br><br>Gender Portion", 
      "titlefont": {
        "color": "", 
        "family": "", 
        "size": 0
      }, 
      "width": 1000, 
      "xaxis": {
        "anchor": "x", 
        "autorange": True, 
        "autotick": True, 
        "domain": [0, 1], 
        "dtick": 1, 
        "exponentformat": "B", 
        "gridcolor": "#eee", 
        "gridwidth": 1, 
        "linecolor": "#444", 
        "linewidth": 1, 
        "mirror": False, 
        "nticks": 0, 
        "overlaying": False, 
        "position": 0, 
        "range": [-0.5, 18.5], 
        "rangemode": "normal", 
        "showexponent": "all", 
        "showgrid": False, 
        "showline": False, 
        "showticklabels": True, 
        "tick0": 0, 
        "tickangle": "auto", 
        "tickcolor": "#444", 
        "tickfont": {
          "color": "", 
          "family": "", 
          "size": 0
        }, 
        "ticklen": 5, 
        "ticks": "", 
        "tickwidth": 1, 
        "title": "", 
        "titlefont": {
          "color": "", 
          "family": "", 
          "size": 0
        }, 
        "type": "category", 
        "zeroline": False, 
        "zerolinecolor": "#444", 
        "zerolinewidth": 1
      }, 
      "yaxis": {
        "anchor": "y", 
        "autorange": True, 
        "autotick": False, 
        "domain": [0, 1], 
        "dtick": 10, 
        "exponentformat": "B", 
        "gridcolor": "#eee", 
        "gridwidth": 1, 
        "linecolor": "#444", 
        "linewidth": 1, 
        "mirror": False, 
        "nticks": 0, 
        "overlaying": False, 
        "position": 0, 
        "range": [0, 105.263157895], 
        "rangemode": "normal", 
        "showexponent": "all", 
        "showgrid": False, 
        "showline": False, 
        "showticklabels": True, 
        "tick0": 0, 
        "tickangle": "auto", 
        "tickcolor": "#444", 
        "tickfont": {
          "color": "", 
          "family": "", 
          "size": 0
        }, 
        "ticklen": 5, 
        "ticks": "", 
        "tickwidth": 1, 
        "title": "% gender", 
        "titlefont": {
          "color": "", 
          "family": "", 
          "size": 0
        }, 
        "type": "linear", 
        "zeroline": False, 
        "zerolinecolor": "#444", 
        "zerolinewidth": 1
      }
    }
    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, world_readable=True)


def make_age_table(titles,avgage):
    values = [[titles],[avgage]]

    trace0 = go.Table(
      type = 'table',
      columnorder = [1,2],
      columnwidth = [80,100],
      header = dict(
        values = [['<b>Titles</b>'],
                      ['<b>Average Age</b>']],
        line = dict(color = '#ffffff'),
        fill = dict(color = '##003b4d'),
        align = ['left','center'],
        font = dict(color = 'white', size = 12),
        height = 40
      ),
      cells = dict(
        values = values,
        line = dict(color = '#ffffff'),
        fill = dict(color = ['#0099cc', 'white']),
        align = ['left', 'center'],
        font = dict(color = '#000000', size = 12),
        height = 30
        ))

    data = [trace0]

    py.plot(data, filename = "Age chart",world_readable=True)





# def process_command(command):
def process_command(command):
    resultlist = []
    command = command.split()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    select = ""
    aggr = ""
    from_ = ""
    join = ""
    group = ""
    where = ""
    insertion = ""
    if command[0] == "luckystar":
        select = "select * "
        from_ = "from Users "
        if command[1] != "all":
            givenareas = command[1].split(',')
            where = "where Area in ( " + "?"+",?"*(len(givenareas)-1)+" ) "   
            insertion = givenareas      
        statement = select+aggr+from_+join+group+where 
        cur.execute(statement,insertion)

        range_ = 0
        users = []
        for row in cur:
            range_ +=1
            userinfo = {'name':row[1],'userlink':row[2],'area':row[3],'age':row[4],'gender':row[5],'signuptime':row[6]}
            users.append(Host(userinfo))
        random = randint(0,range_)
        user = users[random]

        return user

    if command[0] == "number":
        areas = []
        resultnumbers = []
        select = "select AreaName, ResultNumber "
        from_ = "from Areas "
        if command[1] != "all":
            givenareas = command[1].split(',')
            where = "where AreaName in ( " + "?"+",?"*(len(givenareas)-1)+" ) "
            insertion = givenareas
        statement = select+aggr+from_+join+group+where 
        cur.execute(statement,insertion)
        for row in cur:
            areas.append(row[0])
            resultnumbers.append(row[1])

        make_number_chart(areas,resultnumbers)
        return resultnumbers

    if command[0] == "gender":
        titles = []
        maleportion = []
        femaleportion = []
        select = "select Gender, count(Gender),Area "
        from_ = "from Users "
        group = "group by Gender,Area "

        if command[1] != "all":
            givenareas = command[1].split(",")
            where = "having Area in ("+"?"+",?"*(len(givenareas)-1)+") "
            insertion = givenareas

        statement = select+aggr+from_+join+group+where
        cur.execute(statement,insertion)

        genderdis = {}
        for row in cur:
            if row[2] not in genderdis:
                genderdis[row[2]]={}
            if row[0] == "Male":
                genderdis[row[2]][row[0]] = row[1]
            if row[0] == "Female":
                genderdis[row[2]][row[0]] = row[1]

        for a in genderdis:
            titles.append(a)
            maleportion.append(genderdis[a]["Male"]/(genderdis[a]["Female"]+genderdis[a]["Male"]))
            femaleportion.append(genderdis[a]["Female"]/(genderdis[a]["Female"]+genderdis[a]["Male"]))

        make_gender_chart(titles,maleportion,femaleportion)
        return titles


        #exclud unspecified age   


    if command[0] == "age":
        titles = []
        avgage = []
        select = "select avg(Age) "
        from_ = "from Users "
        group = "group by "

        if command[1] == "area":
            select +=", Area "
            group += "Area "
            if command[2] != "all":
                givenareas = command[2].split(",")
                where = "having Area in ("+"?"+",?"*(len(givenareas)-1)+") "
                insertion = givenareas   
                print(select+aggr+from_+join+group+where)
            statement = select+aggr+from_+join+group+where
            cur.execute(statement,insertion)

        if command[1] == "gender":
            select+=", Gender "
            group +=" Gender "

            if command[2] != "all":
                givenareas = command[2].split(",")
                where = "where Area in ("+"?"+",?"*(len(givenareas)-1)+") "
                insertion = givenareas
                print(select+aggr+from_+join+group+where)
####
            statement = select+aggr+from_+join+where+group
            cur.execute(statement,insertion)
        agedis = {}
        for row in cur:
            if type(row[0]) != type("abc"):
                titles.append(row[1])
                avgage.append(round(row[0],1))

        make_age_table(titles, avgage)


    conn.close()

    return titles







#interactive prompt
def interactive_prompt():
    help_text = "possible commands:\n"
    help_text += "possible commands:\n"
    response = ''

    while response != 'exit':
        response = input('Enter a command: ')
        if response != 'exit':
            if response == 'help':
                print(help_text)
                continue

            try:
                result = process_command(response)
                if result ==[] or result == None:
                    print("An error happened.\nThe keywords are not valid or the system failed to retrieve corresponding data with given criteria.\nPlease try again.")        

            except:
                print("An error happened.\nThe keywords are not valid or the system failed to retrieve corresponding data with given criteria.\nPlease try again.")

            




def load_data_for_area(area):
    parser = Parser()
    result = parser.get_resultnumber_userlinks(area)
    usersinfolist = []
    resultsnumber = result[0]
    for a in result[1]:
        usersinfolist.append(parser.get_user_info(a))
    insert_pyobject_data_into_db(area,resultsnumber,usersinfolist)


if __name__ == "__main__":
    parser = Parser()
    interactive_prompt()

    # process_command()
    # process_command('gender area unitedstates')
    # process_command('gender area india,japan')
    # process_command('number india,unitedstates')
    # process_command('age area japan,unitedstates')
    # process_command('age gender all')
    # process_command('age gender japan')

