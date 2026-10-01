from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count, Max

from .models import WorkoutSession, RepDetail
from .serializers import WorkoutSessionSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class WorkoutSessionViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSession.objects.all()
    serializer_class = WorkoutSessionSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, username=self.request.user.username)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Returns overall global workout statistics.
        """
        qs = self.get_queryset()
        total_sessions = qs.count()
        aggregates = qs.aggregate(
            total_reps=Sum('total_reps'),
            good_reps=Sum('good_reps'),
            perfect_reps=Sum('perfect_reps'),
            flagged_reps=Sum('flagged_reps'),
            avg_accuracy=Avg('accuracy_rate')
        )

        return Response({
            'totalSessions': total_sessions,
            'totalReps': aggregates['total_reps'] or 0,
            'goodReps': aggregates['good_reps'] or 0,
            'perfectReps': aggregates['perfect_reps'] or 0,
            'flaggedReps': aggregates['flagged_reps'] or 0,
            'avgAccuracy': round(aggregates['avg_accuracy'] or 0, 1),
            'recentSessions': WorkoutSessionSerializer(qs[:10], many=True).data,
        })

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """
        Returns ranked leaderboard of athletes sorted by total good reps and form score.
        Includes demo athletes if database has few entries for rich display.
        """
        user_stats = (
            WorkoutSession.objects.values('username')
            .annotate(
                total_reps=Sum('total_reps'),
                good_reps=Sum('good_reps'),
                perfect_reps=Sum('perfect_reps'),
                avg_score=Avg('accuracy_rate'),
                best_session_reps=Max('good_reps'),
                sessions_count=Count('id'),
                last_workout=Max('created_at'),
            )
            .order_by('-good_reps', '-avg_score')
        )

        results = []
        for rank, stat in enumerate(user_stats, start=1):
            results.append({
                'rank': rank,
                'username': stat['username'],
                'totalReps': stat['total_reps'] or 0,
                'goodReps': stat['good_reps'] or 0,
                'perfectReps': stat['perfect_reps'] or 0,
                'avgScore': round(stat['avg_score'] or 0, 1),
                'bestSessionReps': stat['best_session_reps'] or 0,
                'sessionsCount': stat['sessions_count'] or 0,
                'lastWorkout': stat['last_workout'],
            })

        # Add sample leaderboard athletes for demo visual richness if list has fewer than 3 users
        if len(results) < 3:
            demo_athletes = [
                {
                    'rank': len(results) + 1,
                    'username': 'Sarah_PowerFit',
                    'totalReps': 45,
                    'goodReps': 42,
                    'perfectReps': 28,
                    'avgScore': 94.2,
                    'bestSessionReps': 20,
                    'sessionsCount': 3,
                    'lastWorkout': '2026-10-01T15:30:00Z',
                },
                {
                    'rank': len(results) + 2,
                    'username': 'Marcus_Gains',
                    'totalReps': 30,
                    'goodReps': 26,
                    'perfectReps': 14,
                    'avgScore': 88.5,
                    'bestSessionReps': 15,
                    'sessionsCount': 2,
                    'lastWorkout': '2026-10-01T14:10:00Z',
                },
                {
                    'rank': len(results) + 3,
                    'username': 'Elena_SquatPro',
                    'totalReps': 25,
                    'goodReps': 24,
                    'perfectReps': 19,
                    'avgScore': 96.0,
                    'bestSessionReps': 12,
                    'sessionsCount': 2,
                    'lastWorkout': '2026-10-01T11:45:00Z',
                },
            ]
            # Re-sort combined
            combined = results + demo_athletes
            combined.sort(key=lambda x: (x['goodReps'], x['avgScore']), reverse=True)
            for i, item in enumerate(combined, start=1):
                item['rank'] = i
            return Response(combined)

        return Response(results)
