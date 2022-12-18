from django.db import models


class BaseModel(models.Model):
    """Базовая модель, используемая для создания других"""
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        abstract = True
