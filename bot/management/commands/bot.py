from django.core.management.base import BaseCommand
from .botusr.parser import Parser
from .botusr.vkbot import Parsing_bot
from django.conf import settings as conf
import threading


class Command(BaseCommand):
    help = 'Parsing Bot fot Glory'

    def handle(self, *args, **options):                 
        parser = Parser(
            conf.DEFAULT_PARSER_HTML,
            conf.TODAY_SENDED,
            conf.SEND_AFTER,
            conf.PRELOAD_CACHE
        )
        bot = Parsing_bot(conf.TOKEN_BOT, conf.GROUP_ID, parser)

        threading._start_new_thread(bot.start,(conf.DELAY_RECONECT_VK,))
        
        parser.cicle_check_lessons(bot,conf.DELAY_CHECK)
            