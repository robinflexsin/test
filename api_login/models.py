from django.db import models

from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from rest_framework.authtoken.models import Token


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address.')

        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username.')

        account = self.model(
            email=self.normalize_email(email), username=kwargs.get('username')
        )

        account.set_password(password)
        account.save()

        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)

        account.is_superuser = True
        try:
            group = Group.objects.get(id=3)
            account.groups.add(group)
        except Exception as e:
            print (e)
        account.save()

        return account


class MarketSector(models.Model):
    sector_name = models.CharField(max_length=100)
    sector_exchange_abbrev = models.CharField(max_length=100, blank=True, null=True)
    sector_exchange_name = models.CharField(max_length=100, blank=True, null=True)
    sector_description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "market_sector"


class User(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=False)
    phone = models.CharField(max_length=15, default=None, blank=True, null=True)
    office_phone = models.CharField(max_length=15, default=None, blank=True, null=True)
    mobile_phone = models.CharField(max_length=15, default=None, blank=True, null=True)
    nfa = models.CharField(max_length=50, default=None, blank=True, null=True)
    firm_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    firm_nfa = models.CharField(max_length=50, default=None, blank=True, null=True)
    markets_traded = models.ForeignKey(MarketSector, default=None, blank=True, null=True, on_delete=models.CASCADE)
    biography = models.CharField(max_length=255, default=None, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=55, blank=True, null=True)
    profile_img = models.FileField(upload_to='images/', max_length=254, blank=True, null=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        return ' '.join([self.first_name, self.last_name])

    def get_short_name(self):
        return self.first_name

    class Meta:
        db_table = "auth_user"

# User._meta.get_field('email')._unique = True

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class CQGOnBoardingDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cqg_web_api_username = models.CharField(max_length=55)
    account_id = models.IntegerField()
    balance = models.DecimalField(max_digits=9, decimal_places=2)
    currency = models.CharField(max_length=20)
    total_value = models.DecimalField(max_digits=9, decimal_places=2)
    ote = models.DecimalField(max_digits=9, decimal_places=2)
    upl = models.DecimalField(max_digits=9, decimal_places=2)
    mvo = models.DecimalField(max_digits=9, decimal_places=2)
    cash_excess = models.DecimalField(max_digits=9, decimal_places=2)
    collateral = models.DecimalField(max_digits=9, decimal_places=2)
    initial_margin = models.DecimalField(max_digits=9, decimal_places=2)
    onboard_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cqg_onboarding_details"


class OnboardFail(models.Model):
    email = models.EmailField()
    onboard_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "onboard_fail"