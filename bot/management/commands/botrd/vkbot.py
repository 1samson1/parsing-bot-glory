from bot.models import Profile, Subscribe
import vk_api
from .messages import VkBotMessages
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import random
from .decor import error_log
from .logs import Log
from time import sleep


class Parsing_bot:
    """ Класс бота ВК"""

    def __init__(self, token, group_id, pars):
        self.pars = pars
        self.vk = vk_api.VkApi(token=token)
        self.longpoll = VkBotLongPoll(self.vk, group_id=group_id)
        self.commands = [] 

    def start(self, delay_reconect):
        Log.write("Bot started")
        while True:
            try:
                for event in self.longpoll.listen():
                    self.entry(event)
            except:
                sleep(delay_reconect)
                Log.write("Reconect to VK")

    @error_log
    def entry(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            profile, add_user_done = Profile.objects.get_or_create(
                external_id=event.obj.message['peer_id'])
            if add_user_done:
                self.get_commands(profile, VkBotMessages.HELLO.value)
            elif 'text' in event.obj.message and event.obj.message['text'] != '':
                self.select_action(event, profile)

    def select_action(self, event, profile):
        """ Bot's menu """

        cmd_spl = event.obj.message['text'].split()

        if event.from_user:
            cmd = cmd_spl[0].lower()
        else:
            cmd = cmd_spl[0].lower()[1::]

        if event.from_user or ((cmd_spl[0].lower()[0] == "/") and self.is_admin(profile.external_id, event.obj.message['from_id'])):

            for command in self.commands:
                if cmd in command['alias']:
                    return command["command"](self, profile, cmd_spl[1::])

            self.get_commands(profile, VkBotMessages.I_DONT_KNOW.value)

    def get_commands(self, profile, text="", *args, **kargs):
        self.send_msg(profile.external_id, text +
                      "\n".join([com['name']+com['info'] for com in self.commands]))

    def mailing_schedule(self, group, text=""):
        for i in Subscribe.objects.filter(group_subscribe=group['title']):
            self.send_msg(i.profile.external_id, text + f"{group['title']}: \n" + "\n".join(
                [f"{idx+1}. {val}" for idx, val in enumerate(group['lessons'])]))

    def is_admin(self, peer_id, from_id):
        try:
            return [item for item in self.vk.method('messages.getConversationMembers', {'peer_id': peer_id, })['items'] if item['member_id'] == from_id][0].get('is_admin')
        except vk_api.exceptions.ApiError:
            self.send_msg(peer_id, VkBotMessages.NO_ACCESS.value)

    def send_msg(self, id, msg):
        try:
            self.vk.method(
                'messages.send',
                {
                    'peer_id': id,
                    'message': msg if msg != None else"",
                    'random_id': random(),
                }
            )

        except Exception as ex:
            Log.write("Send message denied!")
            Log.write(ex)
