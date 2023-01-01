from django.db import models

class Employee(models.Model):
    dunkin_id = models.CharField(primary_key=True, max_length=50)
    mfi_acc_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

class Source(models.Model):
    dunkin_id = models.CharField(primary_key=True, max_length=50)
    mfi_acc_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

class Payment(models.Model):
    batch_id = models.CharField(max_length=50)
    pay_to = models.ForeignKey(Employee, on_delete=models.CASCADE)
    pay_from = models.ForeignKey(Source, on_delete=models.CASCADE)
    status = models.CharField(default="NOT EXECUTED", max_length=50)