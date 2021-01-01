from bot.models import Profile, Subscribe
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import random

class Parsing_bot:
    """ Класс бота ВК"""

    def __init__(self,token,pars):
        self.pars = pars    
        self.vk = vk_api.VkApi(token=token)    
        self.longpoll = VkLongPoll(self.vk)  
        self.commands = [
            {
                'name':'группы',
                'info':' - список доступных групп',
            },
            {
                'name':'подписки',
                'info':' - список ваших подписок',
            },
            {
                'name':'подписаться',
                'info':' - подписакься на рассылку доступных групп',
            },
            {
                'name':'отписаться',
                'info':' - отписаться от групп',
            },
        ]

    def start(self):
        print("Bot started")
        for event in self.longpoll.listen():
            self.actions(event)
          
    def actions(self,event):
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:                
                profile, add_user_done = Profile.objects.get_or_create(external_id=event.peer_id)
                if add_user_done:
                    self.send_msg(profile.external_id,"Привет, я бот, который следит за рассписание. Вот мои основные команды:\n")
                    self.get_commands(profile.external_id)
                else:
                    self.select_action(event,profile)

    def select_action(self,event,profile): ## Меню бота

        cmd_spl = event.text.split()

        if cmd_spl[0].lower() == self.commands[0]['name']: #показ доступных групп
            self.get_groups(event.peer_id)
        elif cmd_spl[0].lower() == self.commands[1]['name']: #показ подписок пользователя
            self.get_my_sybscribe(event.peer_id,profile)        
        elif cmd_spl[0].lower() == self.commands[2]['name']: #подписка на группы
            self.subscribe(event.peer_id,profile,cmd_spl[1::])        
        elif cmd_spl[0].lower() == self.commands[3]['name']: #отписка от группы
            self.unsubscribe(event.peer_id,profile,cmd_spl[1::])      
        else:
            self.send_msg(event.peer_id,'Я не знаю такой команды посмотрите список моих команд:')
            self.get_commands(event.peer_id)

    def get_commands(self,id):
        self.send_msg(id, "\n".join([com['name']+com['info'] for com in self.commands]))

    def get_groups(self,id):
        self.send_msg(id, "Доступные группы:\n" + "\n".join([f"{idx+1}.{val}" for idx, val in enumerate(self.pars.get_groups())])) 

    def get_my_sybscribe(self,id,profile):
        self.send_msg(id, "Ваши подписки:\n" + "\n".join([f"{idx+1}.{val}" for idx, val in enumerate(Subscribe.objects.filter(profile=profile))]))

    def subscribe(self,id,profile,subs):
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
            self.send_msg(id,response)
        else:
            self.send_msg(id,'Не указаны номера групп для подписки!')
        
    def unsubscribe(self,id,profile,unsubs):
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
            self.send_msg(id,response)
        else:
            self.send_msg(id,'Не указаны номера групп для отподписки!')

    def send_msg(self,peer_id,msg):
        self.vk.method(
            'messages.send',
            {
                'peer_id':peer_id,
                'message':msg if msg != None else"",
                'random_id': random(),
            }
        )
