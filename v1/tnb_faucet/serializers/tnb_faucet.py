from rest_framework import serializers
from ..models.tnb_faucet import FaucetOption
from drf_recaptcha.fields import ReCaptchaV2Field, ReCaptchaV3Field
# from thenewboston.utils.fields import all_field_names
# from ..models.transaction_log import TransactionLog



# class TransactionLogSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = TransactionLog
#         fields = ['id', 'balance_lock', 'amount', 'timestamp']
#         read_only_fields = all_field_names(TransactionLog)

# class TransactionLogDetailSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = TransactionLog
#         fields = '__all__'
#         read_only_fields = all_field_names(TransactionLog)


class FaucetOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaucetOption
        fields = ['id', 'coins', 'delay']


class FormSerializer(serializers.Serializer):
    recaptcha = ReCaptchaV2Field()
    url = serializers.URLField()
    faucet_option_id = serializers.IntegerField()

    def validate(self, attrs):
        attrs.pop("recaptcha")
        return attrs