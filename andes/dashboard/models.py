from django.db import models

#Entity classes are created in the database
class User(models.Model):
    us_name = models.CharField(max_length=75)
    us_contact = models.CharField(max_length=15)
    us_mail = models.EmailField(max_length=95)
    us_hash_pass = models.TextField()
    us_status = models.BinaryField(default=b'\x01')
    class Meta:
        db_table = 'andes_users'

class Sensor(models.Model):
    sen_id = models.AutoField(primary_key=True)
    sen_name = models.CharField(max_length=85)
    sen_type = models.CharField(max_length=45)
    max_capacity = models.IntegerField()
    sen_serialno = models.CharField(max_length=45)
    sen_imei = models.CharField(max_length=45)
    user_us_id = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'andes_sensors'

class Variable(models.Model):
    var_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    var_radiofrecuency = models.IntegerField()
    var_presure = models.DecimalField(max_digits=5, decimal_places=2)
    var_time = models.DateTimeField()
    var_capacity = models.IntegerField() #current % of capacity
    var_battery = models.IntegerField()
    sensors_sen_id = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    localizacion = models.TextField()
    class Meta:
        db_table = 'andes_variables'
