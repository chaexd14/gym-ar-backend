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
        Returns ranked leaderboard of athletes strictly from database records,
        sorted by total good reps and average form score.
        """
        user_stats = (
            WorkoutSession.objects.exclude(username__isnull=True)
            .exclude(username__exact='')
            .values('username')
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

        return Response(results)
