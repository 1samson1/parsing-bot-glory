from datetime import datetime
from django.conf import settings as conf


class Log:
    @classmethod
    def write(cls, text, log_file="logs.txt"):
        format_text= f'[{datetime.today()}] {text}\n'
        print(format_text, end="")
        if conf.LOGS:
            with open(log_file, "a") as log:
                log.write(format_text)
      