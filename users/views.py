from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework import permissions

from users.models import CustomUser
from users.serializers import RegisterSerializer, UserSerializer
# Create your views here.
class NewUserView(CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    

class MeView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user