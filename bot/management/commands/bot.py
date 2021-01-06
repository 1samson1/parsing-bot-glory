from django.core.management.base import BaseCommand
import threading
from .botusr.parser import Parser
from .botusr.vkbot import Parsing_bot
from .botusr.config import token, group_id, default_parser_html, delay_check, delay_reconect_vk


class Command(BaseCommand):
    help = 'Parsing Bot fot Glory'

    def handle(self, *args, **options):                 
        pars = Parser(default_parser_html)
        bot = Parsing_bot(token, group_id, pars)

        threading._start_new_thread(bot.start,(delay_reconect_vk,))
        
        pars.cicle_check_lessons(bot,delay_check)
            