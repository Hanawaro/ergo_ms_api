from rest_framework import serializers
from .models import FieldSetting

class FieldSettingSerializer(serializers.ModelSerializer):
    """Сериализатор пользовательского поля для проектов/задач"""

    class Meta:
        model = FieldSetting
        fields = ['id', 'entity_type', 'name', 'label', 'type']

    def validate(self, attrs):
        entity_type = attrs.get('entity_type', getattr(self.instance, 'entity_type', None))
        name = attrs.get('name', getattr(self.instance, 'name', None))

        if entity_type and name:
            qs = FieldSetting.objects.filter(entity_type=entity_type, name=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'name': 'Поле с таким системным именем уже существует для этого типа сущности.'
                })
        return attrs
