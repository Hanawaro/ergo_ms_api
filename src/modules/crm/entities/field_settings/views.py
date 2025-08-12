# src/modules/crm/views_field_settings.py
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FieldSetting
from .serializers import FieldSettingSerializer


class FieldSettingViewSet(viewsets.ModelViewSet):
    queryset = FieldSetting.objects.all()
    serializer_class = FieldSettingSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['entity_type', 'name', 'type']
    search_fields = ['name', 'label']
    ordering_fields = ['id', 'name', 'label', 'sort_index']
    ordering = ['entity_type', 'sort_index', 'id']

    # ---------- helpers ----------
    def _normalize_payload(self, entity_type: str, items: list):
        if not isinstance(items, list):
            return None, Response({'error': 'fields must be an array'}, status=status.HTTP_400_BAD_REQUEST)

        required = {'name', 'label', 'type'}
        names = []
        norm = []
        for idx, i in enumerate(items):
            if not isinstance(i, dict):
                return None, Response({'error': f'Field #{idx} must be an object'}, status=status.HTTP_400_BAD_REQUEST)
            if not required.issubset(i.keys()):
                return None, Response({'error': f'Field #{idx} must contain {sorted(required)}'}, status=status.HTTP_400_BAD_REQUEST)
            name = (i.get('name') or '').strip()
            label = (i.get('label') or '').strip()
            ftype = i.get('type')
            if not name or not label:
                return None, Response({'error': f'Field #{idx}: name/label must be non-empty'}, status=status.HTTP_400_BAD_REQUEST)
            names.append(name)
            norm.append({
                'entity_type': entity_type,
                'name': name,
                'label': label,
                'type': ftype,
                'sort_index': idx,   # если поля нет в модели, игнорируется ниже
            })
        if len(names) != len(set(names)):
            return None, Response({'error': 'Duplicate "name" in fields'}, status=status.HTTP_400_BAD_REQUEST)
        return norm, None

    def _smart_replace(self, entity_type: str, items: list) -> Response:
        """
        Diff по name:
          - создаём только новые
          - обновляем только изменившиеся (label/type/порядок)
          - удаляем только исчезнувшие
        """
        payload, err = self._normalize_payload(entity_type, items)
        if err:
            return err

        # индексы по name
        desired_by_name = {f['name']: f for f in payload}
        desired_names = set(desired_by_name.keys())

        with transaction.atomic():
            existing_qs = FieldSetting.objects.select_for_update().filter(entity_type=entity_type)
            existing_by_name = {f.name: f for f in existing_qs}
            existing_names = set(existing_by_name.keys())

            to_create_names = desired_names - existing_names
            to_delete_names = existing_names - desired_names
            to_keep_names   = desired_names & existing_names

            # create
            to_create = []
            for n in to_create_names:
                data = desired_by_name[n]
                obj_kwargs = dict(
                    entity_type=entity_type,
                    name=data['name'],
                    label=data['label'],
                    type=data['type'],
                )
                # аккуратно выставляем порядок если поле есть в модели
                if hasattr(FieldSetting, 'sort_index'):
                    obj_kwargs['sort_index'] = data['sort_index']
                to_create.append(FieldSetting(**obj_kwargs))
            if to_create:
                FieldSetting.objects.bulk_create(to_create)

            # update (изменились label/type/порядок)
            to_update = []
            for n in to_keep_names:
                src = desired_by_name[n]
                obj = existing_by_name[n]
                changed = False
                if obj.label != src['label']:
                    obj.label = src['label']; changed = True
                if obj.type != src['type']:
                    obj.type = src['type']; changed = True
                if hasattr(FieldSetting, 'sort_index'):
                    if obj.sort_index != src['sort_index']:
                        obj.sort_index = src['sort_index']; changed = True
                if changed:
                    to_update.append(obj)
            if to_update:
                fields = ['label', 'type']
                if hasattr(FieldSetting, 'sort_index'):
                    fields.append('sort_index')
                FieldSetting.objects.bulk_update(to_update, fields)

            # delete (только те, которых теперь нет)
            if to_delete_names:
                FieldSetting.objects.filter(entity_type=entity_type, name__in=to_delete_names).delete()

            # итог — в желаемом порядке
            qs = FieldSetting.objects.filter(entity_type=entity_type)
            if hasattr(FieldSetting, 'sort_index'):
                qs = qs.order_by('sort_index', 'id')
            else:
                qs = qs.order_by('id')

            data = FieldSettingSerializer(qs, many=True).data
            return Response({'fields': data}, status=status.HTTP_200_OK)

    # ---------- endpoints (ровно 4 метода) ----------
    @action(detail=False, methods=['get'], url_path='projects')
    def list_projects(self, request):
        qs = FieldSetting.objects.filter(entity_type='project')
        if hasattr(FieldSetting, 'sort_index'):
            qs = qs.order_by('sort_index', 'id')
        else:
            qs = qs.order_by('id')
        return Response({'fields': FieldSettingSerializer(qs, many=True).data})

    @action(detail=False, methods=['post'], url_path='projects/replace')
    def replace_projects(self, request):
        return self._smart_replace('project', request.data.get('fields', []))

    @action(detail=False, methods=['get'], url_path='tasks')
    def list_tasks(self, request):
        qs = FieldSetting.objects.filter(entity_type='task')
        if hasattr(FieldSetting, 'sort_index'):
            qs = qs.order_by('sort_index', 'id')
        else:
            qs = qs.order_by('id')
        return Response({'fields': FieldSettingSerializer(qs, many=True).data})

    @action(detail=False, methods=['post'], url_path='tasks/replace')
    def replace_tasks(self, request):
        return self._smart_replace('task', request.data.get('fields', []))
