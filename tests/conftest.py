import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.tasks.models import Task, Category, Tag

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin_user',
        email='admin@example.com',
        password='AdminPassword123!',
        role=User.Role.ADMIN
    )


@pytest.fixture
def manager_user(db):
    return User.objects.create_user(
        username='manager_user',
        email='manager@example.com',
        password='ManagerPassword123!',
        role=User.Role.MANAGER
    )


@pytest.fixture
def member_user_1(db):
    return User.objects.create_user(
        username='member_user_1',
        email='member1@example.com',
        password='MemberPassword123!',
        role=User.Role.MEMBER
    )


@pytest.fixture
def member_user_2(db):
    return User.objects.create_user(
        username='member_user_2',
        email='member2@example.com',
        password='MemberPassword123!',
        role=User.Role.MEMBER
    )


def get_jwt_headers_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.username
    refresh['email'] = user.email
    refresh['role'] = user.role
    return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}


@pytest.fixture
def auth_headers_admin(admin_user):
    return get_jwt_headers_for_user(admin_user)


@pytest.fixture
def auth_headers_manager(manager_user):
    return get_jwt_headers_for_user(manager_user)


@pytest.fixture
def auth_headers_member_1(member_user_1):
    return get_jwt_headers_for_user(member_user_1)


@pytest.fixture
def auth_headers_member_2(member_user_2):
    return get_jwt_headers_for_user(member_user_2)


@pytest.fixture
def category_factory(db):
    def _create_category(owner, name='Engineering', slug='engineering', color='#3B82F6'):
        return Category.objects.create(
            name=name,
            slug=slug,
            owner=owner,
            color=color,
            description=f'Tasks categorized under {name}'
        )
    return _create_category


@pytest.fixture
def tag_factory(db):
    def _create_tag(name='backend', slug='backend', color='#10B981'):
        return Tag.objects.create(
            name=name,
            slug=slug,
            color=color
        )
    return _create_tag


@pytest.fixture
def task_factory(db):
    def _create_task(
        owner,
        title='Implement JWT Auth',
        description='Configure simplejwt endpoints',
        status=Task.Status.TODO,
        priority=Task.Priority.HIGH,
        due_date=None,
        assigned_to=None,
        category=None
    ):
        return Task.objects.create(
            owner=owner,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            assigned_to=assigned_to,
            category=category
        )
    return _create_task
