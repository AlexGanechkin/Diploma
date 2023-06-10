from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    # удаляем этот блок, т.к. в описании поля добавлены параметры auto_now..., которые делают то же самое)
    # def save(self, *args, **kwargs):
    #     if not self.id:  # Когда объект только создается, у него еще нет id
    #         self.created = timezone.now()  # проставляем дату создания
    #     self.updated = timezone.now()  # проставляем дату обновления
    #     return super().save(*args, **kwargs)

    # нужен, чтобы не создавать отдельную таблицу в БД
    class Meta:
        abstract = True
