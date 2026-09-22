import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.tasks.models import Task, Category, Tag

User = get_user_model()


@pytest.mark.django_db
class TestAccountModels:
    def test_create_standard_user(self):
        user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='Password123!',
            role=User.Role.MEMBER
        )
        assert user.username == 'johndoe'
        assert user.email == 'john@example.com'
        assert user.role == User.Role.MEMBER
        assert user.is_member_role is True
        assert user.is_admin_role is False
        assert str(user) == 'johndoe (Member)'

    def test_create_manager_user(self):
        user = User.objects.create_user(
            username='sarahmanager',
            email='sarah@example.com',
            password='Password123!',
            role=User.Role.MANAGER
        )
        assert user.role == User.Role.MANAGER
        assert user.is_manager_role is True
        assert str(user) == 'sarahmanager (Manager)'

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username='superadmin',
            email='admin@test.com',
            password='AdminPass123!'
        )
        assert admin.is_superuser is True
        assert admin.is_staff is True
        assert admin.role == User.Role.ADMIN
        assert admin.is_admin_role is True


@pytest.mark.django_db
class TestTaskModels:
    def test_category_and_tag_creation(self, member_user_1):
        category = Category.objects.create(
            name='DevOps',
            slug='devops',
            owner=member_user_1
        )
        tag = Tag.objects.create(
            name='docker',
            slug='docker'
        )
        assert str(category) == 'DevOps'
        assert str(tag) == '#docker'

    def test_task_creation_and_auto_completion(self, member_user_1):
        task = Task.objects.create(
            owner=member_user_1,
            title='Setup Pytest Specs',
            description='Write full coverage test suites',
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH
        )
        assert task.is_completed is False
        assert task.completed_at is None
        assert '[To Do] Setup Pytest Specs (High)' in str(task)

        # Transition status to COMPLETED
        task.status = Task.Status.COMPLETED
        task.save()
        task.refresh_from_db()

        assert task.is_completed is True
        assert task.completed_at is not None

        # Transition back to IN_PROGRESS
        task.status = Task.Status.IN_PROGRESS
        task.save()
        task.refresh_from_db()

        assert task.is_completed is False
        assert task.completed_at is None
