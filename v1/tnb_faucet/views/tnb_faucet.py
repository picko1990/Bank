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
from ..models.tnb_faucet import FaucetModel, PostModel, FaucetOption
from ..serializers.tnb_faucet import FormSerializer, FaucetOptionSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


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


def validate_post_exists(account_number: str, post_id: int):
    """Same post cannot be used again

    Args:
        account_number (str): TNB public key
        post_id (int): Id of a specific tweet or fb post

    Returns:
        False: If post_id already exists
        account: Account object in the else case
    """
    account, created = Account.objects.get_or_create(
        account_number=account_number,
        defaults={'trust': 0})
    try:
        PostModel.objects.get(post_id=post_id)
        return False
    except PostModel.DoesNotExist:
        return account


def validate_expiry(account: Account, user_id: int):
    """Next valid access time for an account should be less than current time

    Args:
        account (Account): Account object
        user_id (int): Id of a specific twitter or fb user

    Returns:
        FaucetModel: If next_valid_access_time > timezone.now()
        False: Else
    """
    try:
        faucet_model = FaucetModel.objects.filter(
            (Q(account=account) | Q(social_user_id=user_id)),
            next_valid_access_time__gt=timezone.now()
        ).latest('next_valid_access_time')
        return faucet_model
    except FaucetModel.DoesNotExist:
        return False


def error_response(content):
    return {
        "type": "error",
        "content": content
    }


def success_response(content):
    return {
        "type": "success",
        "content": content
    }


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

                    account = validate_post_exists(
                        receiver_account_number,
                        post_id
                    )
                    faucet_model = validate_expiry(account, user_id)

                    if account and not faucet_model:
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
                                    'memo': "Thank you for using TNBExplorer testnet"
                                },
                                {
                                    'amount': bank_config.default_transaction_fee,
                                    'recipient': bank_config.account_number,
                                    'fee': "BANK"
                                },
                                {
                                    'amount': pv_config.default_transaction_fee,
                                    'recipient': pv_config.account_number,
                                    'fee': "PRIMARY_VALIDATOR"
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
                            form = FaucetForm()
                        else:
                            messages.error(
                                request,
                                'Unable to obtain TNB account details!'
                            )
                    else:
                        form = FaucetForm()
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


class API(APIView):

    def get(self, request, format=None):
        queryset = FaucetOption.objects.all()
        serializer = FaucetOptionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = FormSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            try:
                amount = FaucetOption.objects.get(pk=serializer.data['faucet_option_id'])
                url_str = serializer.data['url']

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

                        account = validate_post_exists(
                            receiver_account_number,
                            post_id
                        )
                        faucet_model = validate_expiry(account, user_id)

                        if account and not faucet_model:
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
                                        memo: "Thank you for using TNBExplorer testnet"
                                    },
                                    {
                                        'amount': bank_config.default_transaction_fee,
                                        'recipient': bank_config.account_number,
                                        fee: "BANK"
                                    },
                                    {
                                        'amount': pv_config.default_transaction_fee,
                                        'recipient': pv_config.account_number,
                                        fee: "PRIMARY_VALIDATOR"
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
                                return Response(success_response(
                                    (f'SUCCESS! {amount.coins} faucet funds'
                                     f' transferred to {receiver_account_number}.')
                                ))
                            else:
                                return Response(error_response('Unable to obtain TNB account details!'),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            if faucet_model:
                                duration = (faucet_model.next_valid_access_time
                                            - timezone.now())
                                totsec = duration.total_seconds()
                                h = int(totsec // 3600)
                                m = int((totsec % 3600) // 60)
                                sec = round((totsec % 3600) % 60)
                                return Response(error_response(
                                    ('Slow down! Try again after ('
                                     f'{h} hours {m} mins and {sec} secs'
                                     ') till cooldown period expires.')
                                ), status=status.HTTP_429_TOO_MANY_REQUESTS)
                            else:
                                return Response(error_response(
                                    ('Same post cannot be used again! '
                                     ' Try again with a new one :P')
                                ), status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(error_response(
                            ('Failed to extract information!'
                             ' Make sure post is public,'
                             ' contains #TNBFaucet and your account number')
                        ), status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(error_response('Only facebook and twitter URL allowed!'),
                    status=status.HTTP_400_BAD_REQUEST)
            except FaucetOption.DoesNotExist:
                return Response(error_response('bad request format/data'),
                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(error_response('bad request format/data'),
            status=status.HTTP_400_BAD_REQUEST)
