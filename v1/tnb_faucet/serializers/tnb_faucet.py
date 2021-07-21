# from thenewboston.utils.fields import all_field_names

# from ..models.transaction_log import TransactionLog
from rest_framework import serializers
from ..models.tnb_faucet import FaucetOption


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
    string = serializers.SerializerMethodField()

    class Meta:
        model = FaucetOption
        fields = ['id', 'string']

    def get_string(self, obj):
        return obj.__str__()


class FormSerializer(serializers.Serializer):
    url = serializers.URLField()
    faucet_option_id = serializers.IntegerField()
