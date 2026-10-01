from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import WorkoutSessionViewSet, RegisterView

router = DefaultRouter()
router.register(r'sessions', WorkoutSessionViewSet, basename='workout-session')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Workouts endpoints
    path('workouts/', include(router.urls)),
]
