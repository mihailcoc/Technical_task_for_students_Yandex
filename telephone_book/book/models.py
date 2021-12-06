from django.db import models
from django.core.validators import RegexValidator

from phonenumber_field.modelfields import PhoneNumberField


class Position(models.Model):
    name = models.CharField(verbose_name='Должность', max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class Company(models.Model):
    name = models.CharField(unique=True, verbose_name='Организация', max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.name


class Phone(models.Model):
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    phone_number = PhoneNumberField(validators=[phoneNumberRegex],
        unique=False, null=False, blank=False, db_index=True)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны'

    def __str__(self):
        return self.text


class Employee(models.Model):
    name = models.CharField(
        verbose_name='Имя', db_index=True, max_length=256)
    surname = models.CharField(
        verbose_name='Фамилия', db_index=True, max_length=256)
    patronymic = models.CharField(
        verbose_name='Отчество', db_index=True, max_length=256)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='empoyees',
        verbose_name='Компания сотрудника',
        blank=True,
        null=True
    )
    position = models.ManyToManyField(Position, db_index=True, blank=True)

    work_phone_number = models.ForeignKey(
        Phone,
        on_delete=models.CASCADE,
        related_name='companies',
        verbose_name='Рабочий телефон сотрудника',
        db_index=True, blank=True,
        unique=False
    )
    
    private_phone_number = models.OneToOneField(
        Phone,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Личный телефон сотрудника',
        db_index=True, blank=True, 
        unique=True
    )

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
