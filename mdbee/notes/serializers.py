from mdbee.utils.serializers.base import BaseSerializer
from mdbee.notes.models import Note


class NoteSerializer(BaseSerializer):
    class Meta:
        model = Note
        # fields = '__all__'
        exclude = ['created_on', 'updated_on', 'created_by', 'updated_by']
        lookup_field = 'slug'