from .controllers import *

commands = (
    {
        'name': 'группы',
        'alias': ('группы', 'groups', 'gps', 'group', 'gp'),
        'info': ' - список доступных групп',
        'command': get_groups,
    },
    {
        'name': 'подписки',
        'alias': ('подписки', 'subs'),
        'info': ' - список ваших подписок',
        'command': get_my_sybscribe,
    },
    {
        'name': 'подписаться',
        'alias': ('подписаться', 'sub'),
        'info': ' - подписакься на рассылку доступных групп',
        'command': subscribe,
    },
    {
        'name': 'отписаться',
        'alias': ('отписаться', 'unsub'),
        'info': ' - отписаться от групп',
        'command': unsubscribe,
    },
    {
        'name': 'показать',
        'alias': ('показать', 'show'),
        'info': ' - показать расписание группы',
        'command': show_sch,
    },
    {
        'name': 'помощь',
        'alias': ('помощь', 'help', 'h', 'faq'),
        'info': ' - получить инструкцию использования',
        'command': get_help,
    },
)
