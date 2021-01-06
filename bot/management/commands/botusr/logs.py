from datetime import datetime
from .config import logs


class Log:
    @classmethod
    def write(cls, text, log_file="logs.txt"):
        format_text= f'[{datetime.today()}] {text}\n'
        print(format_text, end="")
        if logs:
            with open(log_file, "a") as log:
                log.write(format_text)
      