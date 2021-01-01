from django.core.management.base import BaseCommand
import threading
from time import sleep
from .bottools.parser import Parser
from .bottools.vkbot import Parsing_bot
from .bottools.token import token


class Command(BaseCommand):
    help = 'Parsing Bot fot Glory'

    def handle(self, *args, **options):                 
        pars = Parser()
        bot = Parsing_bot(token,pars)
        #threading._start_new_thread(bot.start,())
        while True:
            sleep(5)            
            pars.check_lessons(bot)            
            