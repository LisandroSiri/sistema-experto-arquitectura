"""
Módulo de Razonamiento Basado en Casos (CBR).
Implementa el ciclo de las 4Rs: Retrieve, Reuse, Revise, Retain.

Referencia: 
- CBR implica recordar experiencias pasadas y adaptarlas a nuevos problemas.
- En este sistema, cada consulta resuelta se guarda como un "caso" y se
  comparan nuevas consultas con casos similares para mejorar recomendaciones.
"""
import json
import os
from datetime import datetime
from difflib import SequenceMatcher

class CasoBase:
    """
    Base de conocimiento de casos históricos.
    Almacena respuestas del usuario y la recomendación generada.
    """
    
    def __init__(self, ruta_casos=None):
        if ruta_casos is None:
            ruta_casos = os.path.join(os.path.dirname(__file__), '..', 'data', 'cases.json')
        self.ruta = ruta_casos
        self.casos = self._cargar()
    
    def _cargar(self):
        """Carga casos desde JSON."""
        if os.path.exists(self.ruta):
            with open(self.ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"casos": []}
    
    def _guardar(self):
        """Persiste casos a JSON."""
        with open(self.ruta, 'w', encoding='utf-8') as f:
            json.dump(self.casos, f, ensure_ascii=False, indent=2)
    
    def _similitud_atributo(self, val1, val2):
        """Calcula similitud entre dos valores (0-1)."""
        if val1 == val2:
            return 1.0
        if isinstance(val1, str) and isinstance(val2, str):
            return SequenceMatcher(None, val1.lower(), val2.lower()).ratio()
        return 0.0
    
    def _similitud_caso(self, respuestas_nuevas, caso):
        """
        Calcula similitud global entre una consulta nueva y un caso histórico.
        Usa promedio ponderado de similitudes por atributo.
        """
        respuestas_caso = caso.get('respuestas', {})
        atributos_comunes = set(respuestas_nuevas.keys()) & set(respuestas_caso.keys())
        
        if not atributos_comunes:
            return 0.0
        
        suma = sum(
            self._similitud_atributo(respuestas_nuevas[attr], respuestas_caso[attr])
            for attr in atributos_comunes
        )
        
        return suma / len(atributos_comunes)
    
    def recuperar_similares(self, respuestas_nuevas, top_k=3, umbral=0.7):
        """
        Retrieve: Recupera los casos más similares de la base.
        
        Returns:
            Lista de (caso, similitud) ordenada por similitud descendente.
        """
        similitudes = []
        
        for caso in self.casos.get('casos', []):
            sim = self._similitud_caso(respuestas_nuevas, caso)
            if sim >= umbral:
                similitudes.append((caso, sim))
        
        similitudes.sort(key=lambda x: x[1], reverse=True)
        return similitudes[:top_k]
    
    def revisar(self, respuestas_nuevas, recomendacion_nueva, casos_similares):
        """
        Revise: Adapta la recomendación basándose en casos similares.
        
        Returns:
            Recomendación ajustada y nota de adaptación.
        """
        if not casos_similares:
            return recomendacion_nueva, None
        
        # Análisis de casos similares
        stacks_similares = [c['recomendacion']['backend'] for c, _ in casos_similares]
        stack_actual = recomendacion_nueva.get('backend', '')
        
        if stack_actual in stacks_similares:
            return recomendacion_nueva, "Confirmado por casos anteriores similares."
        
        # Si ningún caso similar usó este stack, sugerir alternativa
        nota = (f"Nota CBR: Casos similares anteriores usaron {set(stacks_similares)}. "
                f"Considera revisar si {stack_actual} es la mejor opción para tu contexto.")
        
        return recomendacion_nueva, nota
    
    def retener(self, respuestas, recomendacion, metadatos=None):
        """
        Retain: Almacena un nuevo caso en la base de conocimiento.
        
        Args:
            respuestas: Dict con las respuestas del usuario.
            recomendacion: Dict con la recomendación generada.
            metadatos: Información adicional (timestamp, confianza, etc.)
        """
        nuevo_caso = {
            "id": len(self.casos.get('casos', [])) + 1,
            "timestamp": datetime.now().isoformat(),
            "respuestas": respuestas,
            "recomendacion": {
                "backend": recomendacion.get('backend'),
                "frontend": recomendacion.get('frontend'),
                "bd": recomendacion.get('bd'),
                "deploy": recomendacion.get('deploy')
            },
            "confianza": recomendacion.get('confianza', 0),
            "metadatos": metadatos or {}
        }
        
        self.casos['casos'].append(nuevo_caso)
        self._guardar()
        return nuevo_caso