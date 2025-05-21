from rest_framework import serializers
from .models import Employee, Department, Transaction
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description']

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True
    )
    manager = serializers.StringRelatedField(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source='manager', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Employee
        fields = ['id', 'user', 'phone', 'designation', 'department', 'department_id', 'manager', 'manager_id']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        employee = Employee.objects.create(user=user, **validated_data)
        Transaction.objects.create(
            employee=employee,
            transaction_type='HIRE',
            new_department=employee.department,
        )
        return employee

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TransactionSerializer(serializers.ModelSerializer):
    employee = serializers.StringRelatedField(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source='employee', write_only=True
    )

    previous_department = serializers.StringRelatedField(read_only=True)
    previous_department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='previous_department', write_only=True, required=False, allow_null=True
    )

    new_department = serializers.StringRelatedField(read_only=True)
    new_department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='new_department', write_only=True, required=False, allow_null=True
    )
    class Meta:
        model = Transaction
        fields = ['id', 'employee', 'transaction_type', 'previous_department', 'new_department', 'transaction_date', 'remarks']
        read_only_fields = ['id', 'transaction_date']
      
