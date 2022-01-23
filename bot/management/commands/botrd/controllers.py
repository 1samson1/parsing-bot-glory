from bot.models import Subscribe
from .messages import VkBotMessages


def get_groups(bot, profile, *args, **kargs):
    """ Получение списка групп """

    bot.send_msg(profile.external_id, "Доступные группы:\n" + "\n".join(
        [f"{idx+1}. {val}" for idx, val in enumerate(bot.pars.get_groups())]))


def get_my_sybscribe(bot, profile, *args, **kargs):
    """" Получение подписок пользователя """

    bot.send_msg(profile.external_id, "Ваши подписки:\n" + "\n".join(
        [f"{idx+1}. {val}" for idx, val in enumerate(Subscribe.objects.filter(profile=profile))]))


def subscribe(bot, profile, subs, *args, **kargs):
    """ Подписка на группы """

    response = ''
    groups = bot.pars.get_groups()
    for sub in subs:
        try:
            if 0 < int(sub) < len(groups)+1:
                Subscribe.objects.get_or_create(
                    profile=profile, group_subscribe=groups[int(sub)-1])
                response = f"Подписка на группу {groups[int(sub)-1]} успешно оформлена"
            else:
                response = f"\nГруппы с номером {sub} нет в списке доступных!"

        except ValueError:
            response = f"\n{sub} не является номером группы!"
    if response:
        bot.send_msg(profile.external_id, response)
    else:
        bot.send_msg(profile.external_id, VkBotMessages.NO_GROUP_FOR_SUB.value)


def unsubscribe(bot, profile, unsubs, *args, **kargs):
    """" Отписка от групп """

    response = ''
    subs = Subscribe.objects.filter(profile=profile)
    for unsub in unsubs:
        try:
            if 0 < int(unsub) < len(subs)+1:
                Subscribe.objects.get(
                    profile=profile, group_subscribe=subs[int(unsub)-1].group_subscribe).delete()
                response = f"Подписка на группу {subs[int(unsub)-1].group_subscribe} успешно отменина"
            else:
                response = f"\nГруппы с номером {unsub} нет в списке ваших подписок!"

        except ValueError:
            response = f"\n{unsub} не является номером группы!"

    if response:
        bot.send_msg(profile.external_id, response)
    else:
        bot.send_msg(profile.external_id, VkBotMessages.NO_GROUP_FOR_UNSUB.value)


def show_sch(bot, profile, items, *args, **kargs):
    """ Показать рассписание группы """

    cache = bot.pars.get_cache()[bot.pars.today-1]

    if 0 < int(items[0]) < len(cache)+1:
        bot.send_msg(profile.external_id, "Расписание " + f"{cache[int(items[0])-1]['title']}: \n" + "\n".join(
            [f"{idx+1}. {val}" for idx, val in enumerate(cache[int(items[0])-1]['lessons'])]))
    else:
        bot.send_msg(
            profile.external_id, f"\nГруппы с номером {items[0]} нет в списке доступных!")


def get_help(bot, profile, *args, **kargs):
    """ Получить помощь """

    bot.send_msg(profile.external_id, VkBotMessages.HELP.value)
