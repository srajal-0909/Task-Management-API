import django_filters
from django.utils import timezone
from .models import Task, Category, Tag


class TaskFilter(django_filters.FilterSet):
    """
    Advanced custom query filtering parameters for Task management.
    """
    status = django_filters.ChoiceFilter(choices=Task.Status.choices)
    priority = django_filters.ChoiceFilter(choices=Task.Priority.choices)
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    category_slug = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__id',
        to_field_name='id'
    )
    tag_slug = django_filters.CharFilter(field_name='tags__slug', lookup_expr='exact')

    # Date filtering
    due_date = django_filters.DateFilter(field_name='due_date', lookup_expr='exact')
    due_after = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_before = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    # Status / Completion state
    is_completed = django_filters.BooleanFilter(field_name='is_completed')
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')

    # User associations
    assigned_to = django_filters.NumberFilter(field_name='assigned_to__id')
    assigned_username = django_filters.CharFilter(field_name='assigned_to__username', lookup_expr='iexact')
    owner = django_filters.NumberFilter(field_name='owner__id')

    class Meta:
        model = Task
        fields = [
            'status',
            'priority',
            'category',
            'category_slug',
            'tags',
            'tag_slug',
            'due_date',
            'due_after',
            'due_before',
            'is_completed',
            'is_overdue',
            'assigned_to',
            'assigned_username',
            'owner',
        ]

    def filter_is_overdue(self, queryset, name, value):
        today = timezone.now().date()
        if value is True:
            return queryset.filter(
                due_date__lt=today,
                is_completed=False
            )
        elif value is False:
            return queryset.exclude(
                due_date__lt=today,
                is_completed=False
            )
        return queryset
