from bs4 import BeautifulSoup 
import datetime
import json
import requests as reqs

class Parser:
    """Класс парсера"""
    #https://python-scripts.com/beautifulsoup-html-parsing#web-scraping   
    def __init__(self):        
       self.update()
       self.today_send = False
       self.today = 1

    def update(self):
        try:
            print("Update sheldule")
            self.soup =  BeautifulSoup(reqs.get(f"https://xn--c1akimkh.xn--p1ai/lesson_table_show/?day={self.get_num_day(1)}").text,'lxml')
            #with open("/mnt/d/Projects/Parsing_Bot/src/index.html","r") as file:     
            #    self.soup = BeautifulSoup(file.read(),"lxml") 
        except:
            print("Connection error!")

    def get_cache(self):
        with open('./schedule.json','r') as cache_file:
            return json.load(cache_file)

    def set_cache(self,cache):
        with open('./schedule.json','w') as cache_file:
            json.dump(cache,cache_file)


    def check_lessons(self,bot):
        self.update()
        cache = self.get_cache()
        schedule = self.get_schedule()        
        day = self.soup.select_one('.title-day-shedule').text

        if self.today != self.get_num_day() and datetime.datetime.today().hour > 12:
            self.today = self.get_num_day()
            self.today_send = False

        if not self.today_send:             
            bot.mailing_schedule(schedule,f'Paccписание "{day}" ')
            self.today_send = True
        else:
            if cache[self.get_num_day(1)-1] != schedule:                
                bot.mailing_schedule(
                    [sch for idx,sch in enumerate(schedule) if cache[self.get_num_day(1)-1][idx] != sch],
                    f'Изменения в рассписании "{day}" '
                )

                cache[self.get_num_day(1)-1] = schedule
                self.set_cache(cache)

                self.get_num_day()
                self.today_send = True


    def get_num_day(self,appday=0):
        tomorrow_day = datetime.date.today().isoweekday() + appday

        if tomorrow_day >= 5:
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

        