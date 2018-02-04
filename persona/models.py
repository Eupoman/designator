from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Benefactor(models.Model):
    email = models.EmailField(_('email address'), unique=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("Benefactor")
        verbose_name_plural = _("Benefactors")

class Benefactors(models.Model):
    user = models.OneToOneField(User, related_name="persona")
    benfactors = models.ManyToManyField(Benefactor, related_name="benfactors")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Benefactor user mapping")
        verbose_name_plural = _("Benefactors user mapping")

class UserStatus(models.Model):
    user = models.OneToOneField(User, related_name="persona_user")
    facebook_status = models.DateTimeField(null=True, blank=True)
    twitter_status = models.DateTimeField(null=True, blank=True)
    reddit_status = models.DateTimeField(null=True, blank=True)
    dead_status = models.BooleanField(default=False)
    last_activity = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("User Status")
        verbose_name_plural = _("User's Status")

class SaveOTP(models.Model):
    mobile_number = models.CharField(max_length=15)
    pin = models.CharField(max_length=5)

class BenefactorProfile(models.Model):
    user = models.OneToOneField(User, related_name="benefactor_user")
    phone_number = models.CharField(max_length=15)

class TrainingData(models.Model):
    reason = models.CharField(max_length=150)
    decision = models.BooleanField()

    class Meta:
        verbose_name = _("Training Data")
        verbose_name_plural = _("Training Data")
    def __str__(self):
        return self.reason

