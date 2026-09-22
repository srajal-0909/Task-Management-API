import pytest
from rest_framework.exceptions import ValidationError
from apps.accounts.serializers import UserRegisterSerializer, UserSerializer
from apps.tasks.serializers import TaskSerializer, TaskStatusUpdateSerializer, CategorySerializer
from apps.tasks.models import Task, Category


@pytest.mark.django_db
class TestSerializers:
    def test_user_register_serializer_passwords_mismatch(self):
        payload = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'DifferentPassword456!',
        }
        serializer = UserRegisterSerializer(data=payload)
        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors

    def test_user_register_serializer_success(self):
        payload = {
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
            'role': 'MEMBER'
        }
        serializer = UserRegisterSerializer(data=payload)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.username == 'bob'
        assert user.check_password('SecurePassword123!')

    def test_task_serializer_empty_title_validation(self, member_user_1):
        payload = {
            'title': '   ',
            'description': 'Some description'
        }
        serializer = TaskSerializer(data=payload)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_task_serializer_valid_creation(self, rf, member_user_1):
        request = rf.post('/api/v1/tasks/')
        request.user = member_user_1

        payload = {
            'title': 'Containerize backend',
            'description': 'Write multi-stage Dockerfile and docker-compose.yml',
            'status': Task.Status.IN_PROGRESS,
            'priority': Task.Priority.CRITICAL,
        }
        serializer = TaskSerializer(data=payload, context={'request': request})
        assert serializer.is_valid(), serializer.errors
        task = serializer.save()
        assert task.owner == member_user_1
        assert task.title == 'Containerize backend'
        assert task.priority == Task.Priority.CRITICAL
