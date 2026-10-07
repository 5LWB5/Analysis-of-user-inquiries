from django.db import models


class Ticket(models.Model):
    class Category(models.TextChoices):
        PAYMENT = 'payment', 'Оплата'
        DELIVERY = 'delivery', 'Доставка'
        TECHNICAL = 'technical', 'Техническая проблема'
        OTHER = 'other', 'Другое'

    class Status(models.TextChoices):
        NEW = 'new', 'Новое'
        IN_PROGRESS = 'in_progress', 'В работе'
        RESOLVED = 'resolved', 'Решено'

    subject = models.CharField('Тема', max_length=200)
    description = models.TextField('Описание')
    category = models.CharField(
        'Категория', max_length=20, choices=Category.choices,
        default=Category.OTHER,
    )
    status = models.CharField(
        'Статус', max_length=20, choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'обращение'
        verbose_name_plural = 'обращения'

    def __str__(self):
        return self.subject
