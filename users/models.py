import uuid
from datetime import datetime, timedelta
from random import random

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from shered.models import BaseModel

# Create your models here.

#EXTRA ORDINARY USER
ORDINARY_USER = 'ordinary_user'
MANAGER = 'manager'
ADMIN = 'admin'

#EXTRA AUTH_TYPE_CHOICES
VIA_EMAIL = 'via_email'
VIA_PHONE = 'via_phone'

#EXTRA AUTH_STATUS
NEW = 'new'
CODE_VERIFIED = 'code_verified'
DONE = 'done'
PHONE_STEP = 'phone_step'


class User(AbstractUser, BaseModel):

    #USER_ROLES
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    user_roles = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY_USER)

    #AUTH_TYPE_CHOICES
    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES)

    #AUTH_STATUS

    AUTH_STATUS_CHOISE = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHONE_STEP, PHONE_STEP)
    )
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS_CHOISE, default=NEW)

    #EMEIL
    email = models.EmailField(unique=True, null=True, blank=True)

    #PHONE_NUMBER
    phone_number = models.CharField(max_length=13, unique=True, null=True, blank=True)

    #PHOTO
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'heic', 'heif '])])

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    #extra make a 4simvole code

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(4)])

        UserConfirmation.objects.create(user=self, code=code, verify_type=verify_type)

        return code

    #example check the same username
    def check_username(self):
        if not self.username:
            temp_username = f'instagram-{uuid.uuid4().__str__().split("-")[-1]}'
            while User.objects.filter(username=temp_username):
                temp_username = f'{temp_username}{random.randint(0, 9)}'
            self.username = temp_username

    #example check the email
    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()
            self.email = normalize_email

    def check_pass(self):
        if not self.password:
            temp_password = f'password-{uuid.uuid4().__str__().split("-")[-1]}'
            self.password = temp_password

    def heshing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh_token': str(refresh),
        }

    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.heshing_password()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()
        super(User, self).save(*args, **kwargs)






#EXTRA USERCONFIRMATIONS

PHONE_EXPARE = 2
EMAIL_EXPARE = 5

class UserConfirmation(BaseModel):

    TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL),
    )
    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=31, choices=TYPE_CHOICES)
    user = models.ForeignKey('users.User', models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPARE)
            else:
                self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPARE)

        super(UserConfirmation, self).save(*args, **kwargs)