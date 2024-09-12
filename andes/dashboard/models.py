from django.db import models

#Entity classes are created in the database
class User(models.Model):
    us_name = models.CharField(max_length=75, verbose_name="name of user")
    us_contact = models.CharField(max_length=15, verbose_name= "contact of user")
    us_mail = models.EmailField(max_length=95, verbose_name= "mail of user")
    us_hash_pass = models.TextField(verbose_name= "password of user")
    us_status = models.BinaryField(default=b'\x01', verbose_name= "status of user")
    
    def __str__(self) -> str:
        return f"user: {self.us_name} - contact: {self.us_contact} - mail: {self.us_mail} - pass: {self.us_hash_pass} - stat: {self.us_status}"
    
    class Meta:
        db_table = 'andes_users'

class Sensor(models.Model):
    sen_id = models.AutoField(primary_key=True, verbose_name="id of sensor")
    sen_name = models.CharField(max_length=85, verbose_name="name of sensor")
    sen_type = models.CharField(max_length=45, verbose_name="type of sensor") 
    max_output_force = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name="pressure force in max volume") #psi
    max_masa = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name="maximun masa allowed in kg")
    sen_serialno = models.CharField(max_length=45, verbose_name="serial of sensor")
    sen_imei = models.CharField(max_length=45, null= True, verbose_name="imei of sensor")
    user_us_id = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'andes_sensors'

class Variable(models.Model):
    var_temperature = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="temperature")
    var_radiofrecuency = models.IntegerField(verbose_name="signal")
    var_presure = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="current output of gas")
    var_time = models.DateTimeField(verbose_name="current time")
    var_output_capacity = models.IntegerField(null=True, verbose_name="current output force") #current % of force output
    var_current_capacity = models.IntegerField(null = True, verbose_name="current percentage of gas")
    var_litres = models.DecimalField(max_digits=5, decimal_places=2, null = True, verbose_name="current amount of litres")
    var_battery = models.IntegerField(verbose_name="current percentage battery")
    localizacion = models.CharField(max_length=45, null=True, verbose_name="current location")
    sensors_sen_id = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    class Meta:
        db_table = 'andes_variables'
