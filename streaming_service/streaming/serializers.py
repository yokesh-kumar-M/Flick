from rest_framework import serializers
from .models import TranscodeJob, StreamSession


class TranscodeJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranscodeJob
        fields = '__all__'


class StreamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamSession
        fields = '__all__'


class StartStreamSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    quality = serializers.CharField(max_length=20, default='auto')
