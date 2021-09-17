from django.db import models
from django.utils import timezone


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

    def __str__(self):
        return f"{self.date}"
