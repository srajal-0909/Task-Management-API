import pytest
from django.urls import reverse
from rest_framework import status
from apps.tasks.models import Task


@pytest.mark.django_db
class TestTasksAPI:
    def test_unauthenticated_access_denied(self, api_client):
        url = reverse('tasks:task-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_member_create_task(self, api_client, auth_headers_member_1, member_user_1):
        url = reverse('tasks:task-list')
        payload = {
            'title': 'Build DRF API endpoints',
            'description': 'Implement CRUD, authentication, and permissions',
            'status': 'TODO',
            'priority': 'HIGH',
        }
        response = api_client.post(url, payload, format='json', **auth_headers_member_1)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Build DRF API endpoints'
        assert response.data['owner']['id'] == member_user_1.id

    def test_user_scoped_isolation_between_members(
        self,
        api_client,
        auth_headers_member_1,
        auth_headers_member_2,
        task_factory,
        member_user_1,
        member_user_2
    ):
        # Create tasks for member 1 and member 2
        task_1 = task_factory(owner=member_user_1, title='Member 1 Secret Task')
        task_2 = task_factory(owner=member_user_2, title='Member 2 Secret Task')

        # Member 1 queries task list
        list_url = reverse('tasks:task-list')
        res_m1 = api_client.get(list_url, **auth_headers_member_1)
        assert res_m1.status_code == status.HTTP_200_OK
        m1_task_titles = [item['title'] for item in res_m1.data['results']]
        assert 'Member 1 Secret Task' in m1_task_titles
        assert 'Member 2 Secret Task' not in m1_task_titles

        # Member 1 attempts to retrieve Member 2's task directly
        detail_url_task_2 = reverse('tasks:task-detail', kwargs={'pk': task_2.id})
        res_m1_get_m2 = api_client.get(detail_url_task_2, **auth_headers_member_1)
        assert res_m1_get_m2.status_code == status.HTTP_404_NOT_FOUND

        # Member 1 attempts to delete Member 2's task
        res_m1_del_m2 = api_client.delete(detail_url_task_2, **auth_headers_member_1)
        assert res_m1_del_m2.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_and_manager_oversight(
        self,
        api_client,
        auth_headers_admin,
        auth_headers_manager,
        task_factory,
        member_user_1,
        member_user_2
    ):
        task_1 = task_factory(owner=member_user_1, title='Task 1')
        task_2 = task_factory(owner=member_user_2, title='Task 2')

        list_url = reverse('tasks:task-list')

        # Admin can view all tasks
        res_admin = api_client.get(list_url, **auth_headers_admin)
        assert res_admin.status_code == status.HTTP_200_OK
        assert res_admin.data['count'] == 2

        # Manager can view all tasks
        res_manager = api_client.get(list_url, **auth_headers_manager)
        assert res_manager.status_code == status.HTTP_200_OK
        assert res_manager.data['count'] == 2

    def test_mark_complete_action(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        task = task_factory(owner=member_user_1, title='Pending Task', status=Task.Status.TODO)
        url = reverse('tasks:task-mark-complete', kwargs={'pk': task.id})

        response = api_client.post(url, **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Task.Status.COMPLETED
        assert response.data['is_completed'] is True
        assert response.data['completed_at'] is not None

    def test_update_status_action(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        task = task_factory(owner=member_user_1, title='In Progress Task', status=Task.Status.TODO)
        url = reverse('tasks:task-update-status', kwargs={'pk': task.id})

        response = api_client.patch(url, {'status': Task.Status.IN_PROGRESS}, format='json', **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Task.Status.IN_PROGRESS
        assert response.data['is_completed'] is False

    def test_summary_metrics_endpoint(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        task_factory(owner=member_user_1, title='T1', status=Task.Status.COMPLETED, priority=Task.Priority.HIGH)
        task_factory(owner=member_user_1, title='T2', status=Task.Status.TODO, priority=Task.Priority.LOW)
        task_factory(owner=member_user_1, title='T3', status=Task.Status.IN_PROGRESS, priority=Task.Priority.CRITICAL)

        url = reverse('tasks:task-summary')
        response = api_client.get(url, **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_tasks'] == 3
        assert response.data['completed_tasks'] == 1
        assert response.data['pending_tasks'] == 2
