#### ¿cómo correr el proyecto en mi computadora?  

Hay una guía paso a paso para ejecutar el proyecto en producción utilizando Docker **(pag 1-7)**, y otra para para ejecutarlo en un servidor local **(pag 7-10)**.  

[manual to exec .pdf](https://uniminuto0-my.sharepoint.com/:b:/g/personal/juan_suarez-so_uniminuto_edu_co/EZ1Uoj-pertMoOMVvkrDO9YB-B7wSpkq6uEgX3F1lkS3Cw?e=Lhh86b)  

#### ¿cómo ejecutar el proyecto?  

Debe crear un super usuario para entrar al módulo del administrador con el comando: `py manage.py createsuperuser` para acceder al módulo del administrador.  

![superuser](./cloudhive/templates/static/images/create_super_user.png)

#### otros:  

debe ejecutar el comando: `docker-compose exec django-web python manage.py migrate` para activar todos los servicios de django.

![alt func](https://developer.mozilla.org/es/docs/Learn_web_development/Extensions/Server-side/Django/Home_page/basic-django.png)


