from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Task, Category, Tag
from .serializers import (
    TaskSerializer,
    TaskStatusUpdateSerializer,
    CategorySerializer,
    TagSerializer,
)
from .filters import TaskFilter
from .permissions import IsTaskOwnerOrAdmin, IsCategoryOwnerOrAdmin
from core.pagination import StandardResultsSetPagination


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Tasks with user-scoped isolation, dynamic query filtering, and role-based permissions.
    """
    serializer_class = TaskSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, IsTaskOwnerOrAdmin]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = TaskFilter
    search_fields = ['title', 'description', 'category__name', 'tags__name']
    ordering_fields = ['due_date', 'created_at', 'priority', 'status', 'title', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Enforce user-scoped data security:
        - ADMIN / MANAGER: Access all tasks across the system.
        - MEMBER: Access only tasks owned by or assigned to the current user.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()

        base_queryset = Task.objects.select_related('owner', 'assigned_to', 'category').prefetch_related('tags')

        if user.is_admin_role or user.is_manager_role:
            return base_queryset.all()

        return base_queryset.filter(
            Q(owner=user) | Q(assigned_to=user)
        ).distinct()

    @action(detail=True, methods=['post'], url_path='complete')
    def mark_complete(self, request, pk=None):
        """
        Convenience endpoint to transition task to COMPLETED status.
        """
        task = self.get_object()
        task.status = Task.Status.COMPLETED
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Quick status transition endpoint.
        """
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Aggregate analytical summary of user-scoped tasks.
        """
        queryset = self.get_queryset()
        today = timezone.now().date()

        total = queryset.count()
        completed = queryset.filter(is_completed=True).count()
        pending = queryset.filter(is_completed=False).count()
        overdue = queryset.filter(due_date__lt=today, is_completed=False).count()

        status_breakdown = dict(
            queryset.values_list('status').annotate(count=Count('id'))
        )
        priority_breakdown = dict(
            queryset.values_list('priority').annotate(count=Count('id'))
        )

        return Response({
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'overdue_tasks': overdue,
            'status_breakdown': status_breakdown,
            'priority_breakdown': priority_breakdown,
        })


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Task Categories scoped to authenticated users.
    """
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, IsCategoryOwnerOrAdmin]
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Category.objects.none()
        if user.is_admin_role:
            return Category.objects.all()
        return Category.objects.filter(owner=user)


class TagViewSet(viewsets.ModelViewSet):
    """
    CRUD API for reusable tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
