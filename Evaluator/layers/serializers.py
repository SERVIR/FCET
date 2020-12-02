from rest_framework import serializers
from layers.models import Attribute
from layers.services import legible_covariate_names

class AttributeNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    display_name = serializers.SerializerMethodField()
    class Meta:
        model = Attribute
        fields = ['name', 'display_name']

    def get_display_name(self, obj):
        return legible_covariate_names(obj.name)

