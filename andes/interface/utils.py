# ********************************************* MAIL ZONE **************************************************
def get_mail(sensor):
    """
    the param sensor works to get all the info of the sensor
    the ResultsGasRestante user_id get the id of the user_id of its respective sensor
    the ResultsGasRestante user get all the info of the respective user
    """
    user_id = sensor.user_us_id_id
    user = User.objects.get(id=user_id)
    return send_email(sensor, user)


def send_email(sensor, user):
    # ⛔ It should create a record in the table alerts
    user_name = user.us_name
    user_mail = user.us_mail
    sen_name = sensor.sen_name
    # Define el contexto para la plantilla
    context = {
        'user': user_name,
        'sensor_name': sen_name
    }
    try:
        # Obtiene la plantilla
        template = get_template('email_template.html')  # Ajusta la ruta si es necesario
        content = template.render(context)
        # Define el asunto del correo antes de crear el mensaje
        subject_mail = f"¡Alerta en el cilindro {sen_name}!"
        # Crea el mensaje de correo electrónico
        message = EmailMultiAlternatives(
            subject=subject_mail,
            body='',
            from_email=settings.EMAIL_HOST_USER,
            to=[user_mail],
            cc=[]
        )
        # Adjunta el contenido HTML
        message.attach_alternative(content, 'text/html')
        message.send()
        return True
    except Exception as e:
        return e
    

