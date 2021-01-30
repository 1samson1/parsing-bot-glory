from bot.models import Profile, Subscribe
import vk_api
from .messages import VkBotMessages
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
from random import random
from .decor import error_log
from .logs import Log
from time import sleep

class Parsing_bot:
    """ Класс бота ВК"""

    def __init__(self,token,group_id,pars):
        self.pars = pars    
        self.vk = vk_api.VkApi(token=token)    
        self.longpoll = VkBotLongPoll(self.vk,group_id=group_id)  
        self.commands = [
            {
                'name':'группы',
                'alias':['группы','groups','gps','group','gp'],
                'info':' - список доступных групп',
            },
            {
                'name':'подписки',
                'alias':['подписки','subs'],
                'info':' - список ваших подписок',
            },
            {
                'name':'подписаться',
                'alias':['подписаться','sub'],
                'info':' - подписакься на рассылку доступных групп',
            },
            {
                'name':'отписаться',
                'alias':['отписаться','unsub'],
                'info':' - отписаться от групп',
            },
            {
                'name':'показать',
                'alias':['показать','show'],
                'info':' - показать расписание группы',
            },
            {
                'name':'помощь',
                'alias':['помошь','help','h','faq'],
                'info':' - получить инструкцию использования',
            },
        ]

    def start(self,delay_reconect):
        Log.write("Bot started")
        while True:
            try:
                for event in self.longpoll.listen():
                    self.actions(event)
            except:
                sleep(delay_reconect)
                Log.write("Reconect to VK")
            
                
    @error_log   
    def actions(self,event):        
        if event.type == VkBotEventType.MESSAGE_NEW:                        
            profile, add_user_done = Profile.objects.get_or_create(external_id=event.obj.message['peer_id'])
            if add_user_done:                
                self.get_commands(profile.external_id,VkBotMessages.HELLO.value)
            else:
                self.select_action(event,profile)

    def select_action(self,event,profile):
        """ Bot's menu """

        cmd_spl = event.obj.message['text'].split()

        if event.from_user:
            cmd = cmd_spl[0].lower()
        else:
            cmd = cmd_spl[0].lower()[1::]
        
        if event.from_user or (cmd_spl[0].lower()[0] == "/"): # and  self.is_admin(profile.external_id,event.obj.message['from_id'])):
            if cmd in self.commands[0]['alias']: #показ доступных групп
                self.get_groups(profile.external_id)

            elif cmd in self.commands[1]['alias']: #показ подписок пользователя
                self.get_my_sybscribe(profile)    

            elif cmd in self.commands[2]['alias']: #подписка на группы
                self.subscribe(profile,cmd_spl[1::])     

            elif cmd in self.commands[3]['alias']: #отписка от группы
                self.unsubscribe(profile,cmd_spl[1::])     

            elif cmd in self.commands[4]['alias']: #показать распимание группы
                self.show_sch(profile.external_id,cmd_spl[1])      

            elif cmd in self.commands[5]['alias']: #инструкция
                self.get_help(profile.external_id)      

            else:                
                self.get_commands(profile.external_id,VkBotMessages.I_DONT_KNOW.value)
        
    def get_commands(self,id,text=""):
        self.send_msg(id,text + "\n".join([com['name']+com['info'] for com in self.commands]))

    def get_groups(self,id):
        self.send_msg(id, "Доступные группы:\n" + "\n".join([f"{idx+1}. {val}" for idx, val in enumerate(self.pars.get_groups())])) 

    def get_my_sybscribe(self,profile):
        self.send_msg(profile.external_id, "Ваши подписки:\n" + "\n".join([f"{idx+1}. {val}" for idx, val in enumerate(Subscribe.objects.filter(profile=profile))]))

    def subscribe(self,profile,subs):
        response = ''
        groups = self.pars.get_groups()        
        for sub in subs:
            try:               
                if 0 < int(sub) < len(groups)+1:                    
                    Subscribe.objects.get_or_create(profile = profile,group_subscribe = groups[int(sub)-1])
                    response += f"Подписка на группу {groups[int(sub)-1]} успешно оформлена" 
                else:
                     response += f"\nГруппы с номером {sub} нет в списке доступных!"            

            except ValueError:
                response += f"\n{sub} не является номером группы!"
        if response:
            self.send_msg(profile.external_id,response)
        else:
            self.send_msg(profile.external_id,VkBotMessages.NO_GROUP_FOR_SUB.value)
        
    def unsubscribe(self,profile,unsubs):
        response = ''
        subs = Subscribe.objects.filter(profile=profile)        
        for unsub in unsubs:
            try:               
                if 0 < int(unsub) < len(subs)+1:                    
                    Subscribe.objects.get(profile = profile,group_subscribe = subs[int(unsub)-1].group_subscribe).delete()
                    response += f"Подписка на группу {subs[int(unsub)-1].group_subscribe} успешно отменина" 
                else:
                    response += f"\nГруппы с номером {unsub} нет в списке ваших подписок!"            

            except ValueError:
                response += f"\n{unsub} не является номером группы!"
        
        if response:
            self.send_msg(profile.external_id,response)
        else:
            self.send_msg(profile.external_id,VkBotMessages.NO_GROUP_FOR_UNSUB.value)
    
    def show_sch(self,id,group):
        cache = self.pars.get_cache()[self.pars.get_num_day()-1]
        
        if 0 < int(group) < len(cache)+1:  
            self.send_msg(id,"Расписание " + f"{cache[int(group)-1]['title']}: \n" + "\n".join([f"{idx+1}. {val}" for idx,val in enumerate(cache[int(group)-1]['lessons'])]))
        else:
            self.send_msg(id, f"\nГруппы с номером {group} нет в списке доступных!") 

    def get_help(self,id):
        self.send_msg(id,VkBotMessages.HELP.value)

    def mailing_schedule(self,groups,text=""):
        for gp in groups:            
            for i in Subscribe.objects.filter(group_subscribe=gp['title']):                
                self.send_msg(i.profile.external_id,text + f"{gp['title']}: \n" + "\n".join([f"{idx+1}. {val}" for idx,val in enumerate(gp['lessons'])]))

    def is_admin(self,peer_id,from_id):
        try:
            return [item for item in self.vk.method('messages.getConversationMembers',{'peer_id':peer_id,})['items'] if item['member_id'] == from_id][0].get('is_admin')
        except vk_api.exceptions.ApiError:
            self.send_msg(peer_id,VkBotMessages.NO_ACCESS.value)
    
    def send_msg(self,id,msg):
        try:           
	        self.vk.method(
            	'messages.send',
                {
        	    'peer_id':id,
                    'message':msg if msg != None else"",
                    'random_id': random(),
                }
            )       
            
        except:
            Log.write("Send message denied!")
