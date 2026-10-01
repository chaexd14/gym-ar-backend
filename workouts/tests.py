from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import WorkoutSession, RepDetail

class WorkoutAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_login(self):
        # 1. Register
        res = self.client.post('/api/auth/register/', {
            'username': 'athlete1',
            'email': 'athlete1@example.com',
            'password': 'SecurePassword123!'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # 2. Obtain Token
        token_res = self.client.post('/api/auth/token/', {
            'username': 'athlete1',
            'password': 'SecurePassword123!'
        })
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_res.data)
        self.assertIn('refresh', token_res.data)

    def test_create_and_fetch_workout_session(self):
        payload = {
            "exercise": "Bodyweight Squats",
            "totalReps": 5,
            "goodReps": 4,
            "flaggedReps": 1,
            "accuracyRate": 80.0,
            "startTime": 1727780000000,
            "endTime": 1727780080000,
            "repHistory": [
                {
                    "repNumber": 1,
                    "isGood": True,
                    "minKneeAngle": 94.5,
                    "durationMs": 2200,
                    "issues": []
                },
                {
                    "repNumber": 2,
                    "isGood": False,
                    "minKneeAngle": 108.0,
                    "durationMs": 2100,
                    "issues": [{"id": "DEPTH", "label": "Squat depth was too shallow"}]
                }
            ]
        }

        # Create session
        res = self.client.post('/api/workouts/sessions/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutSession.objects.count(), 1)
        self.assertEqual(RepDetail.objects.count(), 2)

        # Retrieve session list
        list_res = self.client.get('/api/workouts/sessions/')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

        # Retrieve summary stats
        summary_res = self.client.get('/api/workouts/sessions/summary/')
        self.assertEqual(summary_res.status_code, status.HTTP_200_OK)
        self.assertEqual(summary_res.data['totalSessions'], 1)
        self.assertEqual(summary_res.data['totalReps'], 5)
        self.assertEqual(summary_res.data['goodReps'], 4)
