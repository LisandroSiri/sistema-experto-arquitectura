"""
Hechos (Facts) del dominio para el sistema experto.
Cada hecho representa una pieza de información que el usuario proporciona
o que el motor infiere durante el razonamiento.
"""
from experta import Fact

class RespuestaUsuario(Fact):
    """Hecho que almacena una respuesta individual del usuario."""
    pass

class PerfilProyecto(Fact):
    """
    Hecho agregado que representa el perfil completo del proyecto.
    Se construye a partir de las respuestas del usuario.
    """
    pass

class RecomendacionStack(Fact):
    """
    Hecho que representa una recomendación generada por el motor.
    """
    pass

class ConflictoDetectado(Fact):
    """
    Hecho que representa un conflicto entre requerimientos.
    """
    pass