from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from thenewboston.constants.network import MIN_POINT_VALUE

from v1.accounts.models.account import Account


class FaucetOption(models.Model):
    coins = models.PositiveIntegerField(blank=False)
    delay = models.PositiveSmallIntegerField(
        blank=False,
        validators=[
            MaxValueValidator(30 * 24),
            MinValueValidator(1),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.coins} coins / {self.delay} hrs'


class FaucetModel(models.Model):
    SOCIAL_TYPES = [
        ('Twitter', 'Twitter'),
        ('Facebook', 'Facebook')
    ]

    account = models.ForeignKey(
        Account,
        blank=False,
        on_delete=models.CASCADE
    )
    social_type = models.CharField(
        blank=False,
        max_length=8,
        choices=SOCIAL_TYPES
    )
    social_user_id = models.PositiveBigIntegerField(
        blank=False,
        validators=[
            MinValueValidator(MIN_POINT_VALUE),
        ]
    )
    next_valid_access_time = models.DateTimeField(blank=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    class Meta:
        indexes = [
            models.Index(fields=['next_valid_access_time']),
            models.Index(fields=['account', 'social_user_id']),
        ]
        unique_together = [
            ['social_user_id', 'account'],
            ['social_type', 'account'],
            ['social_type', 'social_user_id']
        ]

    def __str__(self):
        return (
            f'<{self.social_type} : {self.social_user_id}> | '
            f'<{self.account}>'
        )


class PostModel(models.Model):
    post_id = models.PositiveBigIntegerField(
        blank=False,
        validators=[
            MinValueValidator(MIN_POINT_VALUE),
        ]
    )
    reward = models.ForeignKey(
        FaucetOption,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    social_user = models.ForeignKey(
        FaucetModel,
        blank=False,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=['post_id']),
        ]
        unique_together = [['post_id', 'social_user']]

    def __str__(self):
        return (
            f'Sent {self.reward.coins} coins '
            f'to <{self.social_user} | '
            f'via {self.post_id}>'
        )
