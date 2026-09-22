from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.accounts.serializers import UserSerializer
from .models import Task, Category, Tag

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for metadata tags.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color', 'created_at')
        read_only_fields = ('id', 'created_at')


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for grouping categories.
    """
    owner = UserSerializer(read_only=True)
    task_count = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'color', 'owner', 'task_count', 'created_at')
        read_only_fields = ('id', 'owner', 'created_at', 'task_count')

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    """
    Primary serializer for Task CRUD operations.
    """
    owner = UserSerializer(read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        required=False,
        write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        required=False,
        allow_null=True,
        write_only=True
    )
    category = CategorySerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        required=False,
        allow_null=True,
        write_only=True
    )
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'status',
            'priority',
            'due_date',
            'estimated_hours',
            'owner',
            'assigned_to_id',
            'assigned_to',
            'category_id',
            'category',
            'tag_ids',
            'tags',
            'is_completed',
            'completed_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'owner',
            'is_completed',
            'completed_at',
            'created_at',
            'updated_at',
        )

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Task title cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        # Automatically assign the request user as the task owner
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for updating only task status and progression.
    """
    class Meta:
        model = Task
        fields = ('id', 'status', 'is_completed', 'completed_at', 'updated_at')
        read_only_fields = ('id', 'is_completed', 'completed_at', 'updated_at')
