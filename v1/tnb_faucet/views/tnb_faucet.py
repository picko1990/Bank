from datetime import timedelta
from urllib.parse import urlparse


import requests
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from thenewboston.blocks.block import generate_block
from thenewboston.verify_keys.verify_key import encode_verify_key

from v1.accounts.models.account import Account
from v1.blocks.serializers.block import BlockSerializerCreate
from v1.self_configurations.helpers.signing_key import get_signing_key
from v1.self_configurations.models.self_configuration import SelfConfiguration
from ..core import fb_post, tw_post
from ..forms.forms import FaucetForm
from ..models.tnb_faucet import FaucetModel, PostModel


def get_platform(url_str: str):
    platform = None
    url = urlparse(url_str)
    if ((url.netloc == 'www.facebook.com')
        or (url.netloc == 'www.fb.com')
        or (url.netloc == 'facebook.com')
        or (url.netloc == 'fb.com')
        or (url.netloc == 'm.facebook.com')
            or (url.netloc == 'mbasic.facebook.com')):
        platform = fb_post
    elif ((url.netloc == 'twitter.com')
          or (url.netloc == 'www.twitter.com')
          or (url.netloc == 'mobile.twitter.com')
          or (url.netloc == 'm.twitter.com')):
        platform = tw_post
    return platform


def validate_post_exists_or_delay(account_number: str, post_id: int, user_id: int):
    """Enforcing rules before releasing coins

    Rules:
        Same post cannot be used again
        Next valid access time for an account should be less than current time

    Args:
        account_number (str): TNB public key
        post_id (int): Id of a specific tweet or fb post
        user_id (int): Id of a specific twitter or fb user

    Returns:
        False: If post_id already exists or next_valid_access_time > timezone.now()
        account: Account object in the else case
    """
    account, created = Account.objects.get_or_create(
        account_number=account_number,
        defaults={'trust': 0})
    try:
        PostModel.objects.get(post_id=post_id)
        return False
    except PostModel.DoesNotExist:
        try:
            FaucetModel.objects.filter(
                (Q(account=account) | Q(social_user_id=user_id)),
                next_valid_access_time__gt=timezone.now()
            ).latest('next_valid_access_time')
            return False
        except FaucetModel.DoesNotExist:
            return account


def faucet_view(request):
    form = FaucetForm()
    if request.method == 'POST':
        form = FaucetForm(request.POST)
        if form.is_valid():
            # form data
            url_str = form.cleaned_data['url']
            amount = form.cleaned_data['amount']

            platform = get_platform(url_str)
            if platform:
                post = platform.process(url_str, amount)

                if post:
                    receiver_account_number = post.get_account_number()
                    post_id = post.get_id()
                    platform = post.get_platform()
                    user_id = post.get_user()

                    bank_config = SelfConfiguration.objects.first()
                    pv_config = bank_config.primary_validator

                    signing_key = get_signing_key()
                    sender_account_number = encode_verify_key(
                        verify_key=signing_key.verify_key)

                    account = validate_post_exists_or_delay(
                        receiver_account_number,
                        post_id,
                        user_id
                    )
                    if account:
                        response = requests.get((
                            f'{pv_config.protocol}://{pv_config.ip_address}'
                            f':{pv_config.port}'f'/accounts/'
                            f'{sender_account_number}/balance_lock'))

                        if response.status_code == 200:
                            balance_lock = response.json().get('balance_lock')
                            if not balance_lock:
                                balance_lock = bank_config.node_identifier

                            faucet_model, created = (
                                FaucetModel.objects.update_or_create(
                                    account=account,
                                    social_user_id=user_id,
                                    social_type=platform,
                                    defaults={
                                        'next_valid_access_time': (
                                            timezone.now()
                                            + timedelta(hours=amount.delay))
                                    })
                            )

                            post_model, created = PostModel.objects.get_or_create(
                                post_id=post_id,
                                reward=amount,
                                social_user=faucet_model
                            )

                            transactions = [
                                {
                                    'amount': amount.coins,
                                    'recipient': receiver_account_number,
                                },
                                {
                                    'amount': bank_config.default_transaction_fee,
                                    'recipient': bank_config.account_number,
                                },
                                {
                                    'amount': pv_config.default_transaction_fee,
                                    'recipient': pv_config.account_number,
                                }
                            ]

                            block = generate_block(
                                account_number=signing_key.verify_key,
                                balance_lock=balance_lock,
                                signing_key=signing_key,
                                transactions=transactions
                            )
                            serializer = BlockSerializerCreate(
                                data=block,
                                context={'request': request},
                            )
                            serializer.is_valid(raise_exception=True)
                            block = serializer.save()
                            messages.success(
                                request,
                                (f'SUCCESS! {amount.coins} faucet funds'
                                 f' transferred to {receiver_account_number}.'))
                            form = None
                        else:
                            messages.error(
                                request,
                                'Unable to obtain TNB account details!'
                            )
                    else:
                        form = None
                        if faucet_model:
                            duration = (faucet_model.next_valid_access_time
                                        - timezone.now())
                            totsec = duration.total_seconds()
                            h = int(totsec // 3600)
                            m = int((totsec % 3600) // 60)
                            sec = round((totsec % 3600) % 60)
                            messages.error(
                                request,
                                ('Slow down! Try again after ('
                                 f'{h} hours {m} mins and {sec} secs'
                                 ') till cooldown period expires.')
                            )
                        else:
                            messages.error(
                                request,
                                ('Same post cannot be used again! '
                                 ' Try again with a new one :P')
                            )
                else:
                    messages.error(
                        request,
                        ('Failed to extract information!'
                         ' Make sure post is public,'
                         ' contains #TNBFaucet and your account number')
                    )
            else:
                messages.error(
                    request,
                    'Only facebook and twitter URL allowed!')
        else:
            messages.error(
                request,
                'Form invalid! Please provide correct details!'
            )

    context = {
        'form': form
    }
    return render(request, 'index.html', context)
