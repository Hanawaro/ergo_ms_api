from datetime import datetime

from rest_framework import serializers

from src.modules.crm.entities.field_settings.models import FieldSetting
from src.modules.crm.entities.organization_members.models import OrganizationMember
from src.modules.crm.entities.organizations.models import Organization
from src.modules.crm.entities.organizations.serializers import OrganizationSerializer
from src.modules.crm.entities.project_members.serializers import ProjectMemberSerializer
from src.modules.crm.entities.project_priorities.serializers import ProjectPrioritySerializer
from src.modules.crm.entities.project_statuses.serializers import ProjectStatusSerializer
from src.modules.crm.entities.projects.models import Project
from src.modules.crm.entities.users.serializers import CRMUserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор проекта"""

    owner = CRMUserSerializer(read_only=True)
    manager = CRMUserSerializer(read_only=True)
    manager_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    memberships = ProjectMemberSerializer(many=True, read_only=True)
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)

    # Новые поля для статусов и приоритетов
    status_ref = ProjectStatusSerializer(read_only=True)
    priority_ref = ProjectPrioritySerializer(read_only=True)
    status_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    priority_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    # Дополнительные поля
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)

    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    custom_fields = serializers.DictField(child=serializers.JSONField(), required=False, default=dict)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'owner', 'manager', 'manager_id',
            'organization', 'organization_id', 'memberships', 'status', 'priority', 'start_date', 'end_date',
            'created_at', 'updated_at', 'color', 'task_count', 'completed_task_count',
            'progress', 'status_ref', 'priority_ref', 'status_ref_id', 'priority_ref_id',
            'current_status', 'current_priority', 'status_display', 'priority_display',
            'custom_fields'
        ]

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_completed_task_count(self, obj):
        """Получить количество завершенных задач (учитываем новую и старую систему статусов)"""
        from django.db.models import Q

        # Фильтр для новой системы статусов (status_ref.is_final = True)
        new_system_filter = Q(status_ref__is_final=True, status_ref__is_active=True)

        # Фильтр для старой системы статусов (status = 'done')
        old_system_filter = Q(status='done')

        return obj.tasks.filter(new_system_filter | old_system_filter).count()

    def get_progress(self, obj):
        """Вычислить прогресс проекта в процентах"""
        total = obj.tasks.count()
        if total == 0:
            return 0

        completed = self.get_completed_task_count(obj)
        return round((completed / total) * 100)

    def _coerce_value(self, ftype, raw):
        if raw in (None, ''):
            return None
        if ftype in ('text', 'textarea'):
            return str(raw)
        if ftype == 'number':
            # допускаем строку с числом
            try:
                num = float(raw)
                # красивее хранить int, если целое
                return int(num) if num.is_integer() else num
            except Exception:
                raise serializers.ValidationError('Ожидалось число')
        if ftype == 'checkbox':
            # true/false/1/0/"true"/"false"
            if isinstance(raw, bool):
                return raw
            if isinstance(raw, (int, float)):
                return bool(raw)
            if isinstance(raw, str):
                val = raw.strip().lower()
                if val in ('true', '1', 'yes', 'on'):
                    return True
                if val in ('false', '0', 'no', 'off'):
                    return False
            raise serializers.ValidationError('Ожидалось булево значение')
        if ftype == 'date':
            # храним ISO-дату YYYY-MM-DD
            s = str(raw)
            try:
                dt = datetime.strptime(s[:10], '%Y-%m-%d')
                return dt.strftime('%Y-%m-%d')
            except Exception:
                raise serializers.ValidationError('Ожидался формат даты YYYY-MM-DD')
        if ftype == 'datetime':
            # храним ISO 8601
            s = str(raw)
            try:
                # допускаем без таймзоны
                dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
                # нормализуем в ISO без микросекунд
                return dt.replace(microsecond=0).isoformat()
            except Exception:
                raise serializers.ValidationError('Ожидался ISO 8601 datetime')
        # на всякий
        return raw

    def validate_custom_fields(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('custom_fields должен быть объектом')
        # читаем актуальную схему
        schema = FieldSetting.objects.filter(entity_type='project').values('name', 'type')
        allowed = {s['name']: s['type'] for s in schema}

        sanitized = {}
        errors = {}

        # берём только те ключи, которые определены в FieldSetting
        for key, raw in value.items():
            if key not in allowed:
                # можно просто игнорировать неизвестные; здесь выберем «жёстко» — сообщим об ошибке
                errors[key] = 'Поле не описано в FieldSetting'
                continue
            ftype = allowed[key]
            try:
                sanitized[key] = self._coerce_value(ftype, raw)
            except serializers.ValidationError as e:
                errors[key] = str(e)

        if errors:
            raise serializers.ValidationError(errors)
        return sanitized

    # --- create/update: остальное как у вас, custom_fields пройдёт автоматически через validated_data ---
    def create(self, validated_data):
        user = self.context['request'].user
        organization_id = validated_data.pop('organization_id', None)
        if not organization_id:
            raise serializers.ValidationError('organization_id is required')

        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError('Организация не найдена')

        if not (organization.owner == user or
                OrganizationMember.objects.filter(organization=organization, user=user, status='accepted').exists()):
            raise serializers.ValidationError('Вы не являетесь участником организации')

        validated_data['owner'] = user
        validated_data['organization'] = organization
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # обычный update — custom_fields уже провалидирован и попадёт в instance.custom_fields
        return super().update(instance, validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """Сериализатор списка проектов"""

    owner = CRMUserSerializer(read_only=True)
    manager = CRMUserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)

    # Новые поля для статусов и приоритетов
    status_ref = ProjectStatusSerializer(read_only=True)
    priority_ref = ProjectPrioritySerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)

    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    custom_fields = serializers.DictField(child=serializers.JSONField(), read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'owner', 'manager', 'organization', 'status', 'priority',
            'start_date', 'end_date', 'created_at', 'color', 'task_count',
            'completed_task_count', 'progress', 'status_ref', 'priority_ref',
            'current_status', 'current_priority', 'status_display', 'priority_display',
            'custom_fields'
        ]

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_completed_task_count(self, obj):
        """Получить количество завершенных задач (учитываем новую и старую систему статусов)"""
        from django.db.models import Q

        # Фильтр для новой системы статусов (status_ref.is_final = True)
        new_system_filter = Q(status_ref__is_final=True, status_ref__is_active=True)

        # Фильтр для старой системы статусов (status = 'done')
        old_system_filter = Q(status='done')

        return obj.tasks.filter(new_system_filter | old_system_filter).count()

    def get_progress(self, obj):
        """Вычислить прогресс проекта в процентах"""
        total = obj.tasks.count()
        if total == 0:
            return 0

        completed = self.get_completed_task_count(obj)
        return round((completed / total) * 100)