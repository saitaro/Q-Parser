import os

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user."""
        if not email:
            raise ValueError("Users must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and saves a superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email instead of username."""

    favorites = models.ManyToManyField('Apartment', null=True, blank=True)
    email = models.EmailField(max_length=120, unique=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Apartment(models.Model):
    address = models.CharField(db_index=True, max_length=512)
    total_area = models.PositiveSmallIntegerField()
    floor = models.CharField(max_length=7)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.address}, {self.total_area} м², {self.floor}, {self.price} руб/мес'

