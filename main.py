"""
Punto de entrada del sistema experto.
Orquesta: CLI → Motor Experta → CBR → Formateador → Salida.
"""
from engine.knowledge_engine import MotorArquitectura
from engine.facts import RespuestaUsuario
from engine.cbr import CasoBase
from output.formatter import FormateadorSalida
from ui.cli import CLI
import json
import os

def main():
    # 1. Ejecutar interfaz CLI para obtener respuestas
    cli = CLI()
    respuestas = cli.ejecutar()
    
    # 2. Inicializar motor experto y declarar hechos
    motor = MotorArquitectura()
    motor.reset()
    
    for clave, valor in respuestas.items():
        # Convertir listas a string para compatibilidad con Experta
        if isinstance(valor, list):
            valor = ", ".join(valor) if valor else "Ninguna"
        motor.declare(RespuestaUsuario(clave=clave, valor=valor))
    
    # 3. Ejecutar motor de inferencia
    motor.run()
    
    # 4. Obtener recomendación (la primera generada)
    if not motor.recomendaciones:
        print("\n❌ No se pudo generar una recomendación. Revisa tus respuestas.")
        return
    
    recomendacion = motor.recomendaciones[0]
    
    # 5. Aplicar CBR si hay casos similares
    cbr = CasoBase()
    casos_similares = cbr.recuperar_similares(respuestas)
    alertas_cbr = None
    
    if casos_similares:
        recomendacion, alertas_cbr = cbr.revisar(respuestas, recomendacion, casos_similares)
    
    # 6. Formatear salida
    formateador = FormateadorSalida(modo='estudiante')
    salida = formateador.formatear(
        respuestas=respuestas,
        recomendacion=recomendacion,
        conflictos=motor.conflictos,
        casos_similares=casos_similares,
        alertas_cbr=alertas_cbr
    )
    
    print(salida)
    
    # 7. Retener caso para futuras consultas (CBR)
    cbr.retener(respuestas, recomendacion)
    print(f"\n💾 Caso guardado en la base de conocimiento CBR.")
    
    # 8. Exportar resultado como JSON (útil para futura API/React)
    resultado_json = {
        "respuestas": respuestas,
        "recomendacion": recomendacion,
        "conflictos": motor.conflictos,
        "casos_similares": [
            {"id": c['id'], "similitud": s, "stack": c['recomendacion']['backend']}
            for c, s in casos_similares
        ] if casos_similares else []
    }
    
    with open('resultado_consulta.json', 'w', encoding='utf-8') as f:
        json.dump(resultado_json, f, ensure_ascii=False, indent=2)
    
    print("📄 Resultado exportado a 'resultado_consulta.json' (listo para React).")

if __name__ == "__main__":
    main()