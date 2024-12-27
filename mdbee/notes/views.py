from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from mdbee.notes.models import Note
from mdbee.notes.serializers import NoteSerializer
from mdbee.utils.views.base import BaseViewset



class NoteViewSet(BaseViewset):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    
    action_serializers = {
        "default": NoteSerializer,
    }
    
    def filter_queryset(self, queryset):
        queryset = queryset.filter(user=self.request.user)
        return super().filter_queryset(queryset)
    
    permission_classes = [IsAuthenticated]