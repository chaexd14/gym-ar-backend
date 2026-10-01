from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count

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
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Returns aggregated stats across all sessions:
        total squats performed, good reps, flagged reps, average accuracy, total sessions.
        """
        qs = self.get_queryset()
        if request.user.is_authenticated:
            qs = qs.filter(user=request.user)

        total_sessions = qs.count()
        aggregates = qs.aggregate(
            total_reps=Sum('total_reps'),
            good_reps=Sum('good_reps'),
            flagged_reps=Sum('flagged_reps'),
            avg_accuracy=Avg('accuracy_rate')
        )

        return Response({
            'totalSessions': total_sessions,
            'totalReps': aggregates['total_reps'] or 0,
            'goodReps': aggregates['good_reps'] or 0,
            'flaggedReps': aggregates['flagged_reps'] or 0,
            'avgAccuracy': round(aggregates['avg_accuracy'] or 0, 1),
            'recentSessions': WorkoutSessionSerializer(qs[:5], many=True).data,
        })
