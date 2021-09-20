from rest_framework import serializers
from .models import Stat


class StatSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(input_formats=['%Y-%m-%d-%H_%M_%S',], required=False)

    class Meta:
        model = Stat
        fields = "__all__"
