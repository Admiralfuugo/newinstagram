from .serializers import SignUpSerializer
from .views import CreateUserView
from django.urls import path, include

urlpatterns = [
    path('signup/', CreateUserView.as_view()),
]