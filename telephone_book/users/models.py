from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email,and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        try:
            with transaction.atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except CustomUser.DoesNotExist:
            raise ValueError('The given user must be set')

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class UserRole:
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'
        CHOICES = [
            (USER, 'user'),
            (MODERATOR, 'moderator'),
            (ADMIN, 'admin'),
        ]

    username = models.CharField(
        max_length=254,
        verbose_name='Имя пользователя',
        help_text='Введите имя пользователя',
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Адрес электронной почты',
        help_text='Введите email',
        unique=True
    )
    first_name = models.CharField(
        max_length=254,
        verbose_name='Имя',
        help_text='Введите имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=254,
        verbose_name='Фамилия',
        help_text='Введите фамилию',
        blank=True
    )
    bio = models.TextField(
        verbose_name='Биография',
        help_text='Напишите кратко о себе',
        blank=True,
    )
    role = models.CharField(
        max_length=254,
        verbose_name='Статус пользователя',
        help_text='Введите статус пользователя',
        choices=UserRole.CHOICES,
        default=UserRole.USER,
    )
    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        return self

    @property
    def is_admin(self):
        return self.role == self.UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.UserRole.MODERATOR

    class Meta:
        ordering = ['-id', ]

    def __str__(self):
        return self.email
