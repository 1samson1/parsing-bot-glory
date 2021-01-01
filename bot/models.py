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