# GymMentorAR Backend (Django + DRF)

This directory is designated for the post-MVP backend service for GymMentorAR.

## Planned Tech Stack (Post-MVP)
- **Framework**: Django 5.x + Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Authentication**: SimpleJWT (`djangorestframework-simplejwt`) for client and coach roles
- **File Storage**: `django-storages` with AWS S3 / Cloud Storage for workout video clips
- **CORS**: `django-cors-headers` for seamless Next.js frontend communication

## Planned API Endpoints
- `POST /api/auth/token/`: JWT Token obtain
- `POST /api/auth/token/refresh/`: JWT Token refresh
- `POST /api/workouts/sessions/`: Ingest workout summaries & rep metrics exported from the frontend:
  ```json
  {
    "exercise": "Bodyweight Squats",
    "totalReps": 10,
    "goodReps": 9,
    "flaggedReps": 1,
    "accuracyRate": 90,
    "repHistory": [
      {
        "repNumber": 1,
        "isGood": true,
        "minKneeAngle": 96,
        "durationMs": 2400,
        "issues": []
      }
    ],
    "startTime": 1727780000000,
    "endTime": 1727780120000
  }
  ```
- `GET /api/workouts/history/`: Retrieve past session logs & form progress analytics
- `GET /api/coach/clients/`: Coach dashboard data feeds
