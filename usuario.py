class Usuario:
    def __init__(self, id, email, password, pregunta_seguridad, respuesta_seguridad, ha_intercambiado=False):
        self.id = id
        self.email = email
        self.password = password
        self.pregunta_seguridad = pregunta_seguridad
        self.respuesta_seguridad = respuesta_seguridad
        self.ha_intercambiado = ha_intercambiado
    
