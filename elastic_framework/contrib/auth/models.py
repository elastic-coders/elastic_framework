''' Extension of django user implementation
'''

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone



class User(AbstractBaseUser):
    '''base model definition for user authentication
    Define custom model extending this one to add field or other issues
    '''
