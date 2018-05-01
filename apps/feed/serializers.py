from rest_framework import serializers

from apps.feed.models import Pin


class PinSerializers(serializers.ModelSerializer):
    class Meta:
        model = Pin
        fields = '__all__'
