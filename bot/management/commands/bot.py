from django.core.management.base import BaseCommand
from .botusr.parser import Parser
from .botusr.vkbot import Parsing_bot
from .botusr import config as conf
import threading


class Command(BaseCommand):
    help = 'Parsing Bot fot Glory'

    def handle(self, *args, **options):                 
        pars = Parser(conf.default_parser_html,conf.today_send, conf.send_after)
        bot = Parsing_bot(conf.token, conf.group_id, pars)

        threading._start_new_thread(bot.start,(conf.delay_reconect_vk,))
        
        pars.cicle_check_lessons(bot,conf.delay_check)
            