from bs4 import BeautifulSoup 
import datetime
import json
import requests
from .logs import Log
from time import sleep
from .decor import error_log


class Parser:
    """Parser schedule from Glory"""
    
    def __init__(self,parser, today_send=True):        
       self.today_send = today_send
       self.today = self.get_num_day()
       self.parser = parser
       self.__preload_cache()

    def cicle_check_lessons(self,bot,delay):
        while True:
            sleep(delay)            
            self.check_lessons(bot)        

    @error_log
    def __preload_cache(self):   
        Log.write("Preload schedule")
        schedule = []
        for i in range(1,7):
            schedule.append(self.get_schedule(self.load_with_site(i)))
    
        self.set_cache(schedule)
        
    
    def load_with_site(self,day):
        response = requests.get(f"https://xn--c1akimkh.xn--p1ai/lesson_table_show/", params={'day':day})
        if(response.status_code == requests.codes.ok):
            return BeautifulSoup(response.text, self.parser)
        else:
            raise response.raise_for_status()


    def update(self, day):        
        Log.write("Update sheldule")
        self.soup = self.load_with_site(day)          
        

    def get_cache(self):
        with open('./schedule.json','r') as cache_file:
            return json.load(cache_file)

    def set_cache(self,cache):
        with open('./schedule.json','w') as cache_file:
            json.dump(cache,cache_file)

    @error_log
    def check_lessons(self,bot):
        self.update(self.get_num_day(1))
        cache = self.get_cache()
        schedule = self.get_schedule(self.soup)        
        day = self.soup.select_one('.title-day-shedule').text

        if self.today != self.get_num_day():
            self.today = self.get_num_day()
            self.today_send = False

        if not self.today_send and datetime.datetime.today().hour > 12:             
            bot.mailing_schedule(schedule,f'Paccписание "{day}" ')
            Log.write("Send default schedule tomorrow")
            self.today_send = True
        elif cache[self.get_num_day(1)-1] != schedule:                
            bot.mailing_schedule(
                [sch for idx,sch in enumerate(schedule) if cache[self.get_num_day(1)-1][idx] != sch],
                f'Изменения в рассписании "{day}" '
            )

            cache[self.get_num_day(1)-1] = schedule
            self.set_cache(cache)
            
            Log.write("Send updated schedule tomorrow")
            self.today_send = True

    def get_num_day(self,appday=0):
        tomorrow_day = datetime.date.today().isoweekday() + appday

        if tomorrow_day > 5:
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

    def get_schedule(self,soup):                 
        return [self.get_array_lessons(i) for i in soup.find_all("table")]   
        