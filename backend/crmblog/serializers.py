# backend/crmblog/serializers.py
from rest_framework import serializers
from .models.models import Post

class PostSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source='author.email')
    author_id = serializers.ReadOnlyField(source='author.id')
    
    class Meta:
        model = Post
        fields = ['id', 'task_title', 'project_name', 'deadline', 'task_description', 'status', 'author', 'author_id', 'author_email', 'created_at', 'updated_at']
        read_only_fields = ['author', 'author_id', 'author_email']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            validated_data['author'] = request.user
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            instance.author = request.user
        instance.task_title = validated_data.get('task_title', instance.task_title)
        instance.project_name = validated_data.get('project_name', instance.project_name)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.task_description = validated_data.get('task_description', instance.task_description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
