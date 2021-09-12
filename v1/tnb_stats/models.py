from django.db import models


class Stat(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    shift = models.FloatField()
    total = models.IntegerField()
    accounts = models.IntegerField()
    max_balance = models.IntegerField()
    richest = models.CharField(max_length=100)
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
