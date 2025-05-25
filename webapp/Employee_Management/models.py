from django.contrib.auth.models import User
from django.db import models


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email= models.EmailField(unique=True,blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name        

class Transaction(models.Model):
    class transaction_type(models.TextChoices):
        HIRE = 'HIRE', 'Hire'
        TRANSFER = 'TRANSFER', 'Transfer'
        TERMINATION = 'TERMINATION', 'Termination'        

    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=transaction_type.choices)
    previous_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_transactions')
    new_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_transactions')
    transaction_date = models.DateTimeField()
    remarks = models.TextField(blank=True, null=True)    

    def __str__(self):
        return f"{self.employee.name} - {self.transaction_type} on {self.transaction_date}"