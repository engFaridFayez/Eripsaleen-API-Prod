from django.urls import path

from users import views

from .custom_jwt_claims import CustomTokenObtainPairView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/register/', views.NewUserView.as_view(), name='new_user'),
    path('users/me/', views.MeView.as_view(), name='me'),
]