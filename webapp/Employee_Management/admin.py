from django.contrib import admin
from .models import Employee, Department, Transaction

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'designation', 'department', 'manager')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'designation')
    list_filter = ('department',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'transaction_type', 'transaction_date', 'previous_department', 'new_department')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('employee__user__username', 'employee__user__first_name', 'employee__user__last_name')

