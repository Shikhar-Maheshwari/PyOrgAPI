from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Employee, Department, Transaction
from .serializers import (
    EmployeeSerializer,
    DepartmentSerializer,
    TransactionSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'department', 'manager').all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        department_id = self.request.query_params.get('department_id')

        if name:
            queryset = queryset.filter(user__name__icontains=name)
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        return queryset

    @action(detail=True, methods=['put'], url_path='assign-manager')
    def assign_manager(self, request, pk=None):
        employee = self.get_object()
        manager_id = request.data.get('manager_id')
        if not manager_id:
            return Response({'error': 'manager_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            manager = Employee.objects.get(pk=manager_id)
            employee.manager = manager
            employee.save()
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='manager')
    def get_manager(self, request, pk=None):
        employee = self.get_object()
        if not employee.manager:
            return Response(None)
        serializer = self.get_serializer(employee.manager)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='transactions')
    def get_transactions(self, request, pk=None):
        employee = self.get_object()
        transactions = Transaction.objects.filter(employee=employee)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='subordinates')
    def get_subordinates(self, request, pk=None):
        manager = self.get_object()
        subordinates = Employee.objects.filter(manager=manager)
        serializer = self.get_serializer(subordinates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='hierarchy')
    def get_hierarchy(self, request, pk=None):
        manager = self.get_object()
        hierarchy = []

        def fetch_subordinates(mgr):
            subs = Employee.objects.filter(manager=mgr)
            for sub in subs:
                hierarchy.append(sub)
                fetch_subordinates(sub)

        fetch_subordinates(manager)
        serializer = self.get_serializer(hierarchy, many=True)
        return Response(serializer.data)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    @action(detail=True, methods=['get'], url_path='employees')
    def list_employees(self, request, pk=None):
        department = self.get_object()
        employees = Employee.objects.filter(department=department)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('employee', 'previous_department', 'new_department').all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee_id')
        transaction_type = self.request.query_params.get('transaction_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if start_date and end_date:
            queryset = queryset.filter(transaction_date__range=[start_date, end_date])

        return queryset

    def create(self, request, *args, **kwargs):
        employee_id = kwargs.get('pk') or request.data.get('employee')
        employee = get_object_or_404(Employee, pk=employee_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=employee)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
