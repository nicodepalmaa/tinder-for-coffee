from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    milkType = models.CharField(max_length=100)
    recipes = models.JSONField(default=list)