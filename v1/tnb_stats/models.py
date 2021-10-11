from django.db import models
from django.utils import timezone
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save


class CustomStatManager(models.Manager):
    def cached(self):
        return cache.get_or_set("stat_objects", self.all(), 60*60*24)


class Stat(models.Model):
    date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    shift = models.IntegerField()
    total = models.IntegerField()
    accounts = models.IntegerField()
    max_balance = models.IntegerField()
    richest = models.CharField(max_length=64)
    top_5_wealth = models.IntegerField()
    top_5_ownership = models.FloatField()
    top_5_accounts = models.IntegerField()
    top_10_wealth = models.IntegerField()
    top_10_ownership = models.FloatField()
    top_10_accounts = models.IntegerField()
    top_25_wealth = models.IntegerField()
    top_25_ownership = models.FloatField()
    top_25_accounts = models.IntegerField()
    top_50_wealth = models.IntegerField()
    top_50_ownership = models.FloatField()
    top_50_accounts = models.IntegerField()

    objects = CustomStatManager()

    def __str__(self):
        return f"{self.date}"


@receiver(post_save, sender=Stat)
def stat_post_save_handler(sender, **kwargs):
    cache.delete("stat_objects")
