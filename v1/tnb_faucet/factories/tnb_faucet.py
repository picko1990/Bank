from factory import Faker
from factory.django import DjangoModelFactory

from ..models.tnb_faucet import FaucetModel, FaucetOption, PostModel


class FaucetOptionFactory(DjangoModelFactory):
    # account_number = Faker('pystr', max_chars=VERIFY_KEY_LENGTH)
    coins = Faker('pyint', max_value=1500, min_value=1)
    delay = Faker('pyint', max_value=(30 * 24), min_value=1)

    class Meta:
        model = FaucetOption


class FaucetModelFactory(DjangoModelFactory):
    # account
    # social_type
    # social_user_id
    # next_valid_access_time
    # created_at

    class Meta:
        model = FaucetModel


class PostModelFactory(DjangoModelFactory):
    post_id = Faker('pyint', max_value=281474976710656, min_value=1)

    class Meta:
        model = PostModel
