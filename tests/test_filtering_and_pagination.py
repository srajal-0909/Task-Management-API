from datetime import timedelta
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from apps.tasks.models import Task


@pytest.mark.django_db
class TestFilteringAndPagination:
    def test_filter_by_status(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        task_factory(owner=member_user_1, title='Todo Task', status=Task.Status.TODO)
        task_factory(owner=member_user_1, title='Completed Task', status=Task.Status.COMPLETED)

        url = reverse('tasks:task-list')
        response = api_client.get(f"{url}?status=TODO", **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['status'] == Task.Status.TODO

    def test_filter_by_priority(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        task_factory(owner=member_user_1, title='Low Priority Task', priority=Task.Priority.LOW)
        task_factory(owner=member_user_1, title='Critical Priority Task', priority=Task.Priority.CRITICAL)

        url = reverse('tasks:task-list')
        response = api_client.get(f"{url}?priority=CRITICAL", **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['priority'] == Task.Priority.CRITICAL

    def test_filter_by_overdue(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        today = timezone.now().date()
        past_date = today - timedelta(days=5)
        future_date = today + timedelta(days=5)

        task_factory(owner=member_user_1, title='Overdue Task', due_date=past_date, status=Task.Status.IN_PROGRESS)
        task_factory(owner=member_user_1, title='Future Task', due_date=future_date, status=Task.Status.TODO)

        url = reverse('tasks:task-list')
        response = api_client.get(f"{url}?is_overdue=true", **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Overdue Task'

    def test_search_query_parameter(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        task_factory(owner=member_user_1, title='Design Microservice architecture', description='Event-driven')
        task_factory(owner=member_user_1, title='Frontend Tailwind Layout', description='Landing page design')

        url = reverse('tasks:task-list')
        response = api_client.get(f"{url}?search=Microservice", **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Design Microservice architecture'

    def test_ordering_parameter(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        today = timezone.now().date()
        task_factory(owner=member_user_1, title='Task Due Later', due_date=today + timedelta(days=10))
        task_factory(owner=member_user_1, title='Task Due Soon', due_date=today + timedelta(days=1))

        url = reverse('tasks:task-list')
        response = api_client.get(f"{url}?ordering=due_date", **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['title'] == 'Task Due Soon'
        assert response.data['results'][1]['title'] == 'Task Due Later'

    def test_pagination_envelope_and_page_size(self, api_client, auth_headers_member_1, task_factory, member_user_1):
        for i in range(15):
            task_factory(owner=member_user_1, title=f"Pagination Task {i+1}")

        url = reverse('tasks:task-list')
        # Default page_size is 10
        response = api_client.get(url, **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 15
        assert response.data['total_pages'] == 2
        assert response.data['current_page'] == 1
        assert response.data['page_size'] == 10
        assert len(response.data['results']) == 10
        assert response.data['next'] is not None
        assert response.data['previous'] is None

        # Custom page_size query parameter
        res_custom_size = api_client.get(f"{url}?page_size=5", **auth_headers_member_1)
        assert res_custom_size.status_code == status.HTTP_200_OK
        assert res_custom_size.data['total_pages'] == 3
        assert len(res_custom_size.data['results']) == 5
