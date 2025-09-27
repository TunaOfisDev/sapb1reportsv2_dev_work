# backend/authcentral/serializers.py
from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import CustomUser, Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True)
    position = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'is_active', 'is_staff', 'departments', 'position')

    def create(self, validated_data):
        departments_data = validated_data.pop('departments')
        position_data = validated_data.pop('position')
        user = CustomUser.objects.create(**validated_data)
        for department_data in departments_data:
            department, _ = Department.objects.get_or_create(**department_data)
            user.departments.add(department)
        user.position.set(position_data)
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        
        departments_data = validated_data.get('departments')
        if departments_data:
            instance.departments.clear()
            for department_data in departments_data:
                department, _ = Department.objects.get_or_create(**department_data)
                instance.departments.add(department)

        position_data = validated_data.get('position')
        if position_data:
            instance.position.set(position_data)
        
        instance.save()
        return instance