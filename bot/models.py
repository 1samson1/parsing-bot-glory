from django.db import models

# Create your models here.
class Profile(models.Model):
    """Профили пользователей"""

    external_id = models.PositiveIntegerField("ВК ИД")

    def __str__(self):
        return str(self.external_id)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


class Subscribe(models.Model):
    """Подписки пользователей"""

    profile = models.ForeignKey(Profile,verbose_name="Пользователь",on_delete=models.CASCADE)
    group_subscribe = models.CharField("Подписка на группу",max_length=100)

    def __str__(self):
        return self.group_subscribe

    class Meta:
        verbose_name = "Подписки пользователей"
        verbose_name_plural = "Подписки пользователей"

class SendedGroups(models.Model):
    """Группы которым отправлено рассписание"""

    date = models.DateField("Дата", auto_now_add=True)
    group = models.CharField("Группа",max_length=100)

    def __str__(self):
        return self.group
    
    class Meta:
        verbose_name = "Расписание отправленое группам"
        verbose_name_plural = "Расписание отправленое группам"
