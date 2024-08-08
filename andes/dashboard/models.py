from django.db import models

#Entity classes are created in the database
class User(models.Model):
    name = models.CharField(max_length=75)
    contact = models.CharField(max_length=15)
    email = models.EmailField(max_length=95)
    password_hash = models.TextField()
    status = models.BinaryField(default=b'\x01')

class Sensor(models.Model):
    name = models.CharField(max_length=85)
    type = models.CharField(max_length=45)
    max_capacity = models.IntegerField()
    serial_number = models.CharField(max_length=45)
    imei = models.CharField(max_length=45)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Variable(models.Model):
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    radiofrequency = models.IntegerField()
    pressure = models.DecimalField(max_digits=5, decimal_places=2)
    force = models.IntegerField()
    capacity = models.IntegerField()
    battery = models.IntegerField()
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    location = models.TextField()
