'''from rest_framework import serializers
from thenewboston.utils.fields import all_field_names

from ..models.transaction_log import TransactionLog


class TransactionLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionLog
        fields = ['id', 'balance_lock', 'amount', 'timestamp']
        read_only_fields = all_field_names(TransactionLog)

class TransactionLogDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionLog
        fields = '__all__'
        read_only_fields = all_field_names(TransactionLog)'''