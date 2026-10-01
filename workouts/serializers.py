from rest_framework import serializers
from django.contrib.auth.models import User
from .models import WorkoutSession, RepDetail

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class RepDetailSerializer(serializers.ModelSerializer):
    repNumber = serializers.IntegerField(source='rep_number', required=False)
    isGood = serializers.BooleanField(source='is_good', required=False)
    minKneeAngle = serializers.FloatField(source='min_knee_angle', required=False)
    durationMs = serializers.IntegerField(source='duration_ms', required=False)

    class Meta:
        model = RepDetail
        fields = [
            'id',
            'rep_number',
            'repNumber',
            'is_good',
            'isGood',
            'min_knee_angle',
            'minKneeAngle',
            'duration_ms',
            'durationMs',
            'issues'
        ]

    def to_internal_value(self, data):
        # Normalize camelCase to snake_case if incoming from frontend
        normalized = {}
        normalized['rep_number'] = data.get('rep_number', data.get('repNumber', 1))
        normalized['is_good'] = data.get('is_good', data.get('isGood', True))
        normalized['min_knee_angle'] = data.get('min_knee_angle', data.get('minKneeAngle', 180.0))
        normalized['duration_ms'] = data.get('duration_ms', data.get('durationMs', 0))
        normalized['issues'] = data.get('issues', [])
        return super().to_internal_value(normalized)


class WorkoutSessionSerializer(serializers.ModelSerializer):
    repHistory = RepDetailSerializer(source='rep_history', many=True, required=False)
    rep_history = RepDetailSerializer(many=True, required=False)
    totalReps = serializers.IntegerField(source='total_reps', required=False)
    goodReps = serializers.IntegerField(source='good_reps', required=False)
    flaggedReps = serializers.IntegerField(source='flagged_reps', required=False)
    accuracyRate = serializers.FloatField(source='accuracy_rate', required=False)
    startTime = serializers.IntegerField(source='start_time', required=False)
    endTime = serializers.IntegerField(source='end_time', required=False)

    class Meta:
        model = WorkoutSession
        fields = [
            'id',
            'exercise',
            'total_reps',
            'totalReps',
            'good_reps',
            'goodReps',
            'flagged_reps',
            'flaggedReps',
            'accuracy_rate',
            'accuracyRate',
            'start_time',
            'startTime',
            'end_time',
            'endTime',
            'created_at',
            'rep_history',
            'repHistory',
        ]

    def to_internal_value(self, data):
        normalized = {}
        normalized['exercise'] = data.get('exercise', 'Bodyweight Squats')
        normalized['total_reps'] = data.get('total_reps', data.get('totalReps', 0))
        normalized['good_reps'] = data.get('good_reps', data.get('goodReps', 0))
        normalized['flagged_reps'] = data.get('flagged_reps', data.get('flaggedReps', 0))
        normalized['accuracy_rate'] = data.get('accuracy_rate', data.get('accuracyRate', 0.0))
        normalized['start_time'] = data.get('start_time', data.get('startTime'))
        normalized['end_time'] = data.get('end_time', data.get('endTime'))
        
        # Ingest rep list from either key
        reps_data = data.get('repHistory', data.get('rep_history', []))
        normalized['rep_history'] = reps_data

        return super().to_internal_value(normalized)

    def create(self, validated_data):
        reps_data = validated_data.pop('rep_history', [])
        session = WorkoutSession.objects.create(**validated_data)
        
        for rep in reps_data:
            RepDetail.objects.create(session=session, **rep)
            
        return session
