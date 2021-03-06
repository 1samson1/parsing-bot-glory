from django.core.management.base import BaseCommand
from .botrd.parser import Parser
from .botrd.vkbot import Parsing_bot
from django.conf import settings as conf
from .botrd.commands import commands
import threading


class Command(BaseCommand):
    help = 'Parsing Bot for Glory'

    def handle(self, *args, **options):         
        try:        
            parser = Parser(
                conf.DEFAULT_PARSER_HTML,
                conf.TODAY_SENDED,
                conf.SEND_AFTER,
                conf.PRELOAD_CACHE
            )
            bot = Parsing_bot(conf.TOKEN_BOT, conf.GROUP_ID, parser)

            bot.commands = commands

            threading._start_new_thread(bot.start,(conf.DELAY_RECONECT_VK,))
            
            parser.cicle_check_lessons(bot,conf.DELAY_CHECK)
            
        except KeyboardInterrupt:
            print('\n Bot stoped')
            