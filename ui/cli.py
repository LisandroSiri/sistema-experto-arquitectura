"""
Interfaz de línea de comandos (CLI) para el sistema experto.
Usa questionary para prompts interactivos.

NOTA: Este módulo está diseñado para ser reemplazado por un frontend React.
La lógica de negocio está en el motor, no aquí.
La comunicación se hace a través de diccionarios (fácil de serializar a JSON).
"""
import questionary
import json
import os

class CLI:
    """Interfaz de línea de comandos interactiva."""
    
    def __init__(self):
        self.respuestas = {}
        self._cargar_preguntas()
    
    def _cargar_preguntas(self):
        """Carga definición de preguntas desde JSON."""
        ruta = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions.json')
        with open(ruta, 'r', encoding='utf-8') as f:
            self.preguntas_data = json.load(f)
    
    def ejecutar(self):
        """
        Ejecuta el flujo completo de preguntas.
        Retorna el diccionario de respuestas.
        """
        print("\n" + "=" * 60)
        print("🤖 SISTEMA EXPERTO - RECOMENDADOR DE ARQUITECTURA")
        print("=" * 60)
        print("\nResponde las siguientes preguntas para obtener tu recomendación.")
        print("Puedes usar las flechas del teclado y Enter para seleccionar.\n")
        
        for bloque in self.preguntas_data['bloques']:
            print(f"\n📋 BLOQUE {bloque['id']}: {bloque['nombre']}")
            print("-" * 50)
            
            for pregunta in bloque['preguntas']:
                # Verificar condición de branching
                if 'condicion' in pregunta:
                    if not self._evaluar_condicion(pregunta['condicion']):
                        continue  # Saltar pregunta si no cumple condición
                
                respuesta = self._hacer_pregunta(pregunta)
                self.respuestas[pregunta['id']] = respuesta
        
        return self.respuestas
    
    def _evaluar_condicion(self, condicion):
        """
        Evalúa una condición de branching.
        Ej: "tipo_proyecto == 'Web'"
        """
        try:
            # Reemplazar variables con sus valores
            expr = condicion
            for clave, valor in self.respuestas.items():
                expr = expr.replace(clave, repr(valor))
            return eval(expr)
        except:
            return True  # Si falla, mostrar pregunta por defecto
    
    def _hacer_pregunta(self, pregunta):
        """Hace una pregunta y retorna la respuesta."""
        tipo = pregunta.get('tipo', 'single')
        
        if tipo == 'single':
            respuesta = questionary.select(
                pregunta['texto'],
                choices=pregunta['opciones'],
                qmark="❓"
            ).ask()
        
        elif tipo == 'multi':
            respuesta = questionary.checkbox(
                pregunta['texto'],
                choices=pregunta['opciones'],
                qmark="❓"
            ).ask()
            respuesta = ", ".join(respuesta) if respuesta else "Ninguna"
        
        elif tipo == 'text':
            respuesta = questionary.text(
                pregunta['texto'],
                default=pregunta.get('default', ''),
                qmark="❓"
            ).ask()
        
        else:
            respuesta = pregunta.get('default', '')
        
        return respuesta if respuesta is not None else pregunta.get('default', '')