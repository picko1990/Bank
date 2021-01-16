from django.core.validators import MaxValueValidator
from django.db import models
from ...accounts.models.account import Account
from thenewboston.constants.network import BALANCE_LOCK_LENGTH, MAX_POINT_VALUE, VERIFY_KEY_LENGTH
from django.core.validators import MinValueValidator, MaxValueValidator
from thenewboston.constants.network import MIN_POINT_VALUE

class FaucetOption(models.Model):
    coins = models.PositiveIntegerField(blank=False)
    delay = models.PositiveSmallIntegerField(
        blank=False,
        validators=[
            MaxValueValidator(30*24),
            MinValueValidator(1),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f'{self.coins} coins / {self.delay} hrs'
        )

class PostModel(models.Model):
    SOCIAL_TYPES = [
        ('Twitter', 'Twitter'),
        ('Facebook', 'Facebook')
    ]

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
    social_type = models.CharField(blank=False, max_length=8, choices=SOCIAL_TYPES)

    class Meta:
        unique_together = [['post_id', 'social_type']]

    def __str__(self):
        return (
            f'Sent {self.reward.coins} coins '
            f'via <{self.social_type}:{self.post_id}>'
        )


class FaucetModel(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    social_user_id = models.PositiveBigIntegerField(
        blank=False,
        validators=[
            MinValueValidator(MIN_POINT_VALUE),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    next_valid_access_time = models.DateTimeField(blank=False)
    post = models.ManyToManyField(PostModel, blank=False, related_name="social_posts")


    class Meta:
        indexes = [
            # models.Index(fields=['post']),
            models.Index(fields=['next_valid_access_time']),
            models.Index(fields=['account','social_user_id']),
        ]
        unique_together = [['social_user_id', 'account']]

    def __str__(self):
        return (
            f'To {self.account} '
            f'@ {self.social_user_id} | '
        )