from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class CreateNotificationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    notification_type = serializers.CharField(max_length=30)
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    link = serializers.CharField(max_length=500, required=False, default='')
    data = serializers.DictField(required=False, default=dict)
