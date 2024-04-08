from flask import redirect, url_for, session
from usuarioobd import UsuarioOBD

class Autenticador:
    def __init__(self):
       self.usuario_obd = UsuarioOBD()

    def esta_autenticado(self, session):
        return 'email' in session
    
    def redirigir_si_no_autenticado(self):
        if not self.esta_autenticado(session) or not session.get('ha_intercambiado', False):
            return redirect(url_for('index'))
        else:
            return None
   