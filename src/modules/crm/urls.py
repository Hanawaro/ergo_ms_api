from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.crm.entities.field_settings.views import FieldSettingViewSet
from src.modules.crm.entities.crm_notifications.views import CrmNotificationViewSet
from src.modules.crm.entities.organization_invites.views import OrganizationInviteViewSet
from src.modules.crm.entities.organizations.views import OrganizationViewSet
from src.modules.crm.entities.project_priorities.views import ProjectPriorityViewSet
from src.modules.crm.entities.project_statuses.views import ProjectStatusViewSet
from src.modules.crm.entities.projects.views import ProjectViewSet
from src.modules.crm.entities.task_comments.views import TaskCommentViewSet
from src.modules.crm.entities.task_priorities.views import TaskPriorityViewSet
from src.modules.crm.entities.task_statuses.views import TaskStatusViewSet
from src.modules.crm.entities.tasks.views import TaskViewSet
from src.modules.crm.entities.time_logs.views import TimeLogViewSet
from src.modules.crm.entities.users.views import UserViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'task-comments', TaskCommentViewSet)
router.register(r'time-logs', TimeLogViewSet)
router.register(r'users', UserViewSet)
router.register(r'settings/fields', FieldSettingViewSet, basename='field-setting')
router.register(r'notifications', CrmNotificationViewSet, basename='notification')

# Статусы и приоритеты
router.register(r'project-statuses', ProjectStatusViewSet)
router.register(r'project-priorities', ProjectPriorityViewSet)
router.register(r'task-statuses', TaskStatusViewSet)
router.register(r'task-priorities', TaskPriorityViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'invites', OrganizationInviteViewSet, basename='organization-invite')

urlpatterns = [
    path('', include(router.urls)),
]