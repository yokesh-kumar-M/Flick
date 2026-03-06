from rest_framework import serializers
from .models import AccessRequest, AccessGrant


class AccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRequest
        fields = ['id', 'user_id', 'username', 'user_email', 'movie_id', 'movie_title',
                  'status', 'payment_status', 'payment_id', 'email_sent',
                  'access_code', 'reason', 'admin_note',
                  'expires_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'access_code', 'created_at', 'updated_at']


class AccessRequestCreateSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    movie_title = serializers.CharField(max_length=500, required=False, default='')
    reason = serializers.CharField(required=False, default='', allow_blank=True)


class AccessGrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessGrant
        fields = ['id', 'user_id', 'movie_id', 'access_code', 'is_active',
                  'granted_at', 'expires_at']


class VerifyCodeSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    access_code = serializers.CharField(max_length=50)
