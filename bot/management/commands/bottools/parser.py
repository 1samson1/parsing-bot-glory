from bs4 import BeautifulSoup 
import datetime
import json
#import requests as reqs

class Parser:
    """Класс парсера"""
    #https://python-scripts.com/beautifulsoup-html-parsing#web-scraping   
    def __init__(self):        
       self.update()
       self.today_send = False
       self.today = 1

    def update(self):
        print("Update sheldule")
        #self.soup =  BeautifulSoup(reqs.get("https://xn--c1akimkh.xn--p1ai/lesson_table_show/").text,'lxml')
        with open("/mnt/d/Projects/Parsing_Bot/src/index.html","r") as file:     
            self.soup = BeautifulSoup(file.read(),"lxml") 

    def check_lessons(self,bot):
        self.update()
        with open('./schedule.json','r') as cache:
            data = json.load(cache)

        if data[self.get_num_tomorrow()-1] == self.get_schedule():
            
        else:
             

    def get_num_tomorrow(self)
        tomorrow_day = datetime.date.today().isoweekday()
        if tomorrow_day >= 6:
            return 1
        else:
            return tomorrow_day


    def get_groups(self):
        return [i.find("th").text.strip() for i in self.soup.find_all("table")]  

    def get_array_lessons(self,elm):
        """ Get group name and group lessons """       
        
        return {
            "title": elm.find("th").text.strip(),
            "lessons": [i.text.strip() for i in elm.find_all("td")]
        }

    def get_schedule(self):                 
            return [self.get_array_lessons(i) for i in self.soup.find_all("table")]   

        