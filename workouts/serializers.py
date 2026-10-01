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
    isPerfect = serializers.BooleanField(source='is_perfect', required=False)
    minKneeAngle = serializers.FloatField(source='min_knee_angle', required=False)
    durationMs = serializers.IntegerField(source='duration_ms', required=False)
    snapshotImage = serializers.CharField(source='snapshot_image', required=False, allow_null=True, allow_blank=True)
    snapshotReason = serializers.CharField(source='snapshot_reason', required=False, allow_null=True, allow_blank=True)
    snapshotAngle = serializers.FloatField(source='snapshot_angle', required=False, allow_null=True)
    lowestScore = serializers.FloatField(source='lowest_score', required=False, allow_null=True)

    class Meta:
        model = RepDetail
        fields = [
            'id',
            'rep_number',
            'repNumber',
            'is_good',
            'isGood',
            'is_perfect',
            'isPerfect',
            'score',
            'lowest_score',
            'lowestScore',
            'min_knee_angle',
            'minKneeAngle',
            'duration_ms',
            'durationMs',
            'issues',
            'snapshot_image',
            'snapshotImage',
            'snapshot_reason',
            'snapshotReason',
            'snapshot_angle',
            'snapshotAngle',
        ]

    def to_internal_value(self, data):
        normalized = {}
        normalized['rep_number'] = data.get('rep_number', data.get('repNumber', 1))
        normalized['is_good'] = data.get('is_good', data.get('isGood', True))
        normalized['is_perfect'] = data.get('is_perfect', data.get('isPerfect', False))
        normalized['score'] = data.get('score', 100.0)
        normalized['lowest_score'] = data.get('lowest_score', data.get('lowestScore', normalized['score']))
        normalized['min_knee_angle'] = data.get('min_knee_angle', data.get('minKneeAngle', 180.0))
        normalized['duration_ms'] = data.get('duration_ms', data.get('durationMs', 0))
        normalized['issues'] = data.get('issues', [])
        normalized['snapshot_image'] = data.get('snapshot_image', data.get('snapshotImage'))
        normalized['snapshot_reason'] = data.get('snapshot_reason', data.get('snapshotReason'))
        normalized['snapshot_angle'] = data.get('snapshot_angle', data.get('snapshotAngle'))
        return super().to_internal_value(normalized)


class WorkoutSessionSerializer(serializers.ModelSerializer):
    repHistory = RepDetailSerializer(source='rep_history', many=True, required=False)
    rep_history = RepDetailSerializer(many=True, required=False)
    totalReps = serializers.IntegerField(source='total_reps', required=False)
    goodReps = serializers.IntegerField(source='good_reps', required=False)
    perfectReps = serializers.IntegerField(source='perfect_reps', required=False)
    flaggedReps = serializers.IntegerField(source='flagged_reps', required=False)
    accuracyRate = serializers.FloatField(source='accuracy_rate', required=False)
    averageScore = serializers.FloatField(source='average_score', required=False)
    startTime = serializers.IntegerField(source='start_time', required=False)
    endTime = serializers.IntegerField(source='end_time', required=False)

    class Meta:
        model = WorkoutSession
        fields = [
            'id',
            'username',
            'exercise',
            'total_reps',
            'totalReps',
            'good_reps',
            'goodReps',
            'perfect_reps',
            'perfectReps',
            'flagged_reps',
            'flaggedReps',
            'accuracy_rate',
            'accuracyRate',
            'average_score',
            'averageScore',
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
        normalized['username'] = data.get('username', 'Athlete').strip() or 'Athlete'
        normalized['exercise'] = data.get('exercise', 'Bodyweight Squats')
        normalized['total_reps'] = data.get('total_reps', data.get('totalReps', 0))
        normalized['good_reps'] = data.get('good_reps', data.get('goodReps', 0))
        normalized['perfect_reps'] = data.get('perfect_reps', data.get('perfectReps', 0))
        normalized['flagged_reps'] = data.get('flagged_reps', data.get('flaggedReps', 0))
        normalized['accuracy_rate'] = data.get('accuracy_rate', data.get('accuracyRate', 0.0))
        normalized['average_score'] = data.get('average_score', data.get('averageScore', normalized['accuracy_rate']))
        normalized['start_time'] = data.get('start_time', data.get('startTime'))
        normalized['end_time'] = data.get('end_time', data.get('endTime'))
        
        reps_data = data.get('repHistory', data.get('rep_history', []))
        normalized['rep_history'] = reps_data

        return super().to_internal_value(normalized)

    def create(self, validated_data):
        reps_data = validated_data.pop('rep_history', [])
        session = WorkoutSession.objects.create(**validated_data)
        
        for rep in reps_data:
            RepDetail.objects.create(session=session, **rep)
            
        return session
