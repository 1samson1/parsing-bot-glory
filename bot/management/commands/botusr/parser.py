from bs4 import BeautifulSoup 
from datetime import datetime, date, timedelta
import json
import requests
from .logs import Log
from time import sleep
from .decor import error_log
from bot.models import SendedGroups


class Parser:
    """Parser schedule from Glory"""
    
    def __init__(self, parser, today_sended=False, send_after=12, preload_cache=True):        
       self.today = self.get_num_day()
       self.today_sended = today_sended
       self.send_after = send_after
       self.parser = parser
       if preload_cache:
           self.__preload_cache()
       self.update(self.today)

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
        if self.today != self.get_num_day():
            self.today = self.get_num_day()
            self.today_sended = False 

        self.update(self.today)
        cache = self.get_cache()
        schedule = self.get_schedule(self.soup)  
        sended_groups = [sch.group for sch in SendedGroups.objects.filter(date=date.today())]  
        day = self.soup.select_one('.title-day-shedule').text

        if not self.today_sended and len(sended_groups) < len(schedule) and (datetime.today() - timedelta(hours=self.send_after)).hour >= 0:             
            send_groups = []
            for sch in schedule:
                if sch['title'] not in sended_groups:
                    send_groups.append(sch)
                    SendedGroups.objects.get_or_create(group=sch["title"],date=date.today())

            bot.mailing_schedule(
                send_groups,
                f'Paccписание "{day}" '
            )
            
            self.today_sended = True
            Log.write("Send default schedule tomorrow")
        elif cache[self.today-1] != schedule: 

            send_groups = []
            for idx,sch in enumerate(schedule):
                if cache[self.today-1][idx] != sch:
                    send_groups.append(sch)
                    SendedGroups.objects.get_or_create(group=sch["title"],date=date.today())

            bot.mailing_schedule(
                send_groups,
                f'Изменения в рассписании "{day}" '
            )

            cache[self.today-1] = schedule
            self.set_cache(cache)
            
            Log.write("Send updated schedule tomorrow")            

    def get_num_day(self,appday=1):
        tomorrow_day = date.today().isoweekday() + appday

        #if 5 < tomorrow_day < 8:
        #    return 5
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
        
