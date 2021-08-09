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
        self.commands = (
            {
                'name':'группы',
                'alias':('группы','groups','gps','group','gp'),
                'info':' - список доступных групп',
                'command': self.get_groups,
            },
            {
                'name':'подписки',
                'alias':('подписки','subs'),
                'info':' - список ваших подписок',
                'command': self.get_my_sybscribe,
            },
            {
                'name':'подписаться',
                'alias':('подписаться','sub'),
                'info':' - подписакься на рассылку доступных групп',
                'command': self.subscribe,
            },
            {
                'name':'отписаться',
                'alias':('отписаться','unsub'),
                'info':' - отписаться от групп',
                'command': self.unsubscribe,
            },
            {
                'name':'показать',
                'alias':('показать','show'),
                'info':' - показать расписание группы',
                'command': self.show_sch,
            },
            {
                'name':'помощь',
                'alias':('помошь','help','h','faq'),
                'info':' - получить инструкцию использования',
                'command': self.get_help,
            },
        )

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
            elif 'text' in event.obj.message and event.obj.message['text'] != '':
                self.select_action(event,profile)

    def select_action(self,event,profile):
        """ Bot's menu """

        cmd_spl = event.obj.message['text'].split()

        if event.from_user:
            cmd = cmd_spl[0].lower()
        else:
            cmd = cmd_spl[0].lower()[1::]
        
        if event.from_user or ((cmd_spl[0].lower()[0] == "/") and self.is_admin(profile.external_id,event.obj.message['from_id'])):
            
            for command in self.commands:
                if cmd in command['alias']: 
                    return command["command"](profile,cmd_spl[1::])

            self.get_commands(profile,VkBotMessages.I_DONT_KNOW.value)
        
    def get_commands(self, profile, text="", *args, **kargs):
        self.send_msg(profile.external_id,text + "\n".join([com['name']+com['info'] for com in self.commands]))

    def get_groups(self, profile, *args, **kargs):
        self.send_msg(profile.external_id, "Доступные группы:\n" + "\n".join([f"{idx+1}. {val}" for idx, val in enumerate(self.pars.get_groups())])) 

    def get_my_sybscribe(self, profile, *args, **kargs):
        self.send_msg(profile.external_id, "Ваши подписки:\n" + "\n".join([f"{idx+1}. {val}" for idx, val in enumerate(Subscribe.objects.filter(profile=profile))]))

    def subscribe(self, profile, subs, *args, **kargs):
        response = ''
        groups = self.pars.get_groups()        
        for sub in subs:
            try:               
                if 0 < int(sub) < len(groups)+1:                    
                    Subscribe.objects.get_or_create(profile = profile,group_subscribe = groups[int(sub)-1])
                    response = f"Подписка на группу {groups[int(sub)-1]} успешно оформлена" 
                else:
                     response = f"\nГруппы с номером {sub} нет в списке доступных!"            

            except ValueError:
                response = f"\n{sub} не является номером группы!"
        if response:
            self.send_msg(profile.external_id,response)
        else:
            self.send_msg(profile.external_id,VkBotMessages.NO_GROUP_FOR_SUB.value)
        
    def unsubscribe(self, profile, unsubs , *args, **kargs):
        response = ''
        subs = Subscribe.objects.filter(profile=profile)        
        for unsub in unsubs:
            try:               
                if 0 < int(unsub) < len(subs)+1:                    
                    Subscribe.objects.get(profile = profile, group_subscribe = subs[int(unsub)-1].group_subscribe).delete()
                    response = f"Подписка на группу {subs[int(unsub)-1].group_subscribe} успешно отменина" 
                else:
                    response = f"\nГруппы с номером {unsub} нет в списке ваших подписок!"            

            except ValueError:
                response = f"\n{unsub} не является номером группы!"
        
        if response:
            self.send_msg(profile.external_id,response)
        else:
            self.send_msg(profile.external_id,VkBotMessages.NO_GROUP_FOR_UNSUB.value)
    
    def show_sch(self, profile, group, *args, **kargs):
        cache = self.pars.get_cache()[self.pars.today-1]
        
        if 0 < int(group) < len(cache)+1:  
            self.send_msg(profile.external_id,"Расписание " + f"{cache[int(group)-1]['title']}: \n" + "\n".join([f"{idx+1}. {val}" for idx,val in enumerate(cache[int(group)-1]['lessons'])]))
        else:
            self.send_msg(profile.external_id, f"\nГруппы с номером {group} нет в списке доступных!") 

    def get_help(self, profile, *args, **kargs):
        self.send_msg(profile.external_id, VkBotMessages.HELP.value)

    def mailing_schedule(self,group,text=""):
        for i in Subscribe.objects.filter(group_subscribe=group['title']):                
            self.send_msg(i.profile.external_id,text + f"{group['title']}: \n" + "\n".join([f"{idx+1}. {val}" for idx,val in enumerate(group['lessons'])]))

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
            
        except Exception as ex:
            Log.write("Send message denied!")
            Log.write(ex)
