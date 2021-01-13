import requests
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render
from datetime import datetime, timedelta
from ..forms.forms import FaucetForm
from ..core import fb_post, tw_post
from ..models.tnb_faucet import FaucetModel
from v1.accounts.models.account import Account
from v1.banks.models.bank import Bank
from v1.self_configurations.models.self_configuration import SelfConfiguration
from v1.self_configurations.helpers.signing_key import get_signing_key
from v1.tasks.blocks import send_signed_block
from v1.utils.blocks import create_block_and_bank_transactions
from thenewboston.blocks.block import generate_block
from django.utils import timezone
import pytz

def faucet_view(request):
    form = FaucetForm()
    if request.method == 'POST':
        form = FaucetForm(request.POST)
        if form.is_valid():
            # extract data
            url = form.cleaned_data['url']
            amount = form.cleaned_data['amount']

            post = fb_post.process(url)

            receiver_account_number = post.get_account_number()
            post_id = post.get_id()
            platform = post.get_platform()
            user_id = post.get_user()

            bank_config = SelfConfiguration.objects.first()
            pv_config = bank_config.primary_validator
            response = requests.get(f'{pv_config.protocol}://{pv_config.ip_address}:{pv_config.port}/accounts/{receiver_account_number}/balance_lock')
            if not response.status_code == 200:
                print('ERROR')
            balance_lock = response.json().get('balance_lock')
            if not balance_lock:
                balance_lock = receiver_account_number

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

            signing_key = get_signing_key()

            validated_block = generate_block(
                account_number=signing_key.verify_key,
                balance_lock=balance_lock,
                signing_key=signing_key,
                transactions=transactions
            )
            with transaction.atomic():
                account, created = Account.objects.get_or_create(
                    account_number=receiver_account_number,
                    defaults={'trust': 0},
                )
                faucet_model = FaucetModel.objects.filter(
                    Q(account=account) | Q(social_user_id=user_id),
                    next_valid_access_time__gt=datetime.utcnow()
                ).first()
                if not faucet_model:
                    faucet_model, created = FaucetModel.objects.update_or_create(
                        social_type = platform,
                        account = account,
                        social_user_id = user_id,
                        next_valid_access_time = timezone.now() + timedelta(hours=amount.delay)
                    )
                    create_block_and_bank_transactions(validated_block)

                    send_signed_block.delay(
                        block=validated_block,
                        ip_address=pv_config.ip_address,
                        port=pv_config.port,
                        protocol=pv_config.protocol,
                        url_path='/bank_blocks'
                    )
                else:
                    # respond with error
                    pass
    context = {
        'form': form
    }
    return render(request, 'index.html', context)
