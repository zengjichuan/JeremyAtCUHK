from django.db import models

# Create your models here.

class UserInfo(models.Model):
    name = models.CharField(max_length=30)
    emailid = models.IntegerField()
    school = models.CharField(max_length=60)

class EmailList(models.Model):
    email = models.EmailField()

class CheckList(models.Model):
    emailid = models.IntegerField()
    emailqr = models.CharField(max_length=256)
    checkin = models.CharField(max_length=10)

class Relation(models.Model):
    fromid = models.IntegerField()
    toid = models.IntegerField()
