from rest_framework import serializers

from src.modules.crm.entities.organization_members.models import OrganizationMember
from src.modules.crm.entities.organizations.models import Organization
# src/modules/crm/entities/tasks/serializers.py
from datetime import datetime  # <- добавить
from rest_framework import serializers

from src.modules.crm.entities.field_settings.models import FieldSetting  # <- добавить
from src.modules.crm.entities.organization_members.models import OrganizationMember
from src.modules.crm.entities.organizations.models import Organization
from src.modules.crm.entities.organizations.serializers import OrganizationSerializer
from src.modules.crm.entities.projects.models import Project
from src.modules.crm.entities.projects.serializers import ProjectListSerializer
from src.modules.crm.entities.task_attachments.serializers import TaskAttachmentSerializer
from src.modules.crm.entities.task_comments.serializers import TaskCommentSerializer
from src.modules.crm.entities.task_priorities.serializers import TaskPrioritySerializer
from src.modules.crm.entities.task_statuses.serializers import TaskStatusSerializer
from src.modules.crm.entities.tasks.models import Task
from src.modules.crm.entities.time_logs.serializers import TimeLogSerializer
from src.modules.crm.entities.users.serializers import CRMUserSerializer


class TaskListSerializer(serializers.ModelSerializer):
    """Сериализатор списка задач"""

    assignee = CRMUserSerializer(read_only=True)
    creator = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)

    # Новые поля для статусов и приоритетов
    status_ref = TaskStatusSerializer(read_only=True)
    priority_ref = TaskPrioritySerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)

    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()

    # Кастомные поля (только чтение в списке)
    custom_fields = serializers.DictField(child=serializers.JSONField(), read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'creator',
            'status', 'priority', 'start_date', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'estimated_hours', 'actual_hours',
            'kanban_order', 'comment_count', 'attachment_count',
            'status_ref', 'priority_ref', 'current_status', 'current_priority',
            'status_display', 'priority_display', 'parent',
            'custom_fields',
        ]

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_attachment_count(self, obj):
        return obj.attachments.count()


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи"""

    assignee = CRMUserSerializer(read_only=True)
    creator = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project_id = serializers.IntegerField(write_only=True)
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True)
    parent = TaskListSerializer(read_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subtasks = TaskListSerializer(many=True, read_only=True)

    # Новые поля для статусов и приоритетов
    status_ref = TaskStatusSerializer(read_only=True)
    priority_ref = TaskPrioritySerializer(read_only=True)
    status_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    priority_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    # Дополнительные поля
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)

    # Поля дат с дополнительной обработкой
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)

    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    time_logs = TimeLogSerializer(many=True, read_only=True)
    total_time = serializers.SerializerMethodField()

    # Кастомные поля (чтение/запись)
    custom_fields = serializers.DictField(child=serializers.JSONField(), required=False, default=dict)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_id', 'organization', 'organization_id', 'assignee',
            'assignee_id', 'creator', 'status', 'priority', 'start_date', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'estimated_hours', 'actual_hours', 'kanban_order',
            'comments', 'attachments', 'time_logs', 'total_time', 'parent', 'parent_id', 'subtasks',
            'status_ref', 'priority_ref', 'status_ref_id', 'priority_ref_id',
            'current_status', 'current_priority', 'status_display', 'priority_display',
            'custom_fields',
        ]

    def get_total_time(self, obj):
        return sum(log.hours for log in obj.time_logs.all())

    # ---------- custom_fields: валидация и нормализация ----------
    def _coerce_value(self, ftype, raw):
        if raw in (None, ''):
            return None
        if ftype in ('text', 'textarea'):
            return str(raw)
        if ftype == 'number':
            try:
                num = float(raw)
                return int(num) if num.is_integer() else num
            except Exception:
                raise serializers.ValidationError('Ожидалось число')
        if ftype == 'checkbox':
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
            s = str(raw)
            try:
                dt = datetime.strptime(s[:10], '%Y-%m-%d')
                return dt.strftime('%Y-%m-%d')
            except Exception:
                raise serializers.ValidationError('Ожидался формат даты YYYY-MM-DD')
        if ftype == 'datetime':
            s = str(raw)
            try:
                dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
                return dt.replace(microsecond=0).isoformat()
            except Exception:
                raise serializers.ValidationError('Ожидался ISO 8601 datetime')
        return raw

    def validate_custom_fields(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('custom_fields должен быть объектом')

        # схема для задач
        schema = FieldSetting.objects.filter(entity_type='task').values('name', 'type')
        allowed = {s['name']: s['type'] for s in schema}

        sanitized, errors = {}, {}

        for key, raw in value.items():
            if key not in allowed:
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

    # ---------- стандартные validate / create / update ----------
    def validate(self, data):
        if data.get('start_date') and data.get('due_date'):
            if data['due_date'] < data['start_date']:
                raise serializers.ValidationError("Дата окончания не может быть раньше даты начала")
        return data

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

        project_id = validated_data.pop('project_id', None)
        try:
            project = Project.objects.get(id=project_id, organization=organization)
        except Project.DoesNotExist:
            raise serializers.ValidationError('Проект не найден в организации')

        validated_data['project'] = project
        validated_data['creator'] = user
        validated_data['organization'] = organization
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # При PATCH можно «мягко» слить custom_fields (не обязательно, но удобно)
        if self.partial and 'custom_fields' in validated_data:
            new_cf = {**(instance.custom_fields or {}), **validated_data['custom_fields']}
            validated_data['custom_fields'] = new_cf
        return super().update(instance, validated_data)


class TaskCalendarSerializer(serializers.ModelSerializer):
    """Сериализатор задач для календаря"""

    assignee = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'status',
            'priority', 'start_date', 'due_date', 'created_at'
        ]


class TaskKanbanSerializer(serializers.ModelSerializer):
    """Сериализатор задач для канбан доски"""

    assignee = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'status',
            'priority', 'due_date', 'kanban_order', 'estimated_hours'
        ]