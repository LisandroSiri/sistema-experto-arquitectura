"""
Formateador de salida estructurada.
Genera la respuesta en el formato "estilo IA" que solicitaste,
con todas las secciones: análisis, recomendación, alternativas,
riesgos, costos, ruta de escalado, seguridad y testing.
"""

class FormateadorSalida:
    """Genera la salida estructurada del sistema experto."""
    
    def __init__(self, modo='estudiante'):
        """
        Args:
            modo: 'estudiante' (más justificación pedagógica) o
                  'profesional' (respuesta directa y ejecutiva).
        """
        self.modo = modo
    
    def formatear(self, respuestas, recomendacion, conflictos, 
                  casos_similares=None, alertas_cbr=None):
        """Genera la salida completa formateada."""
        lineas = []
        
        # Encabezado
        lineas.append("=" * 70)
        lineas.append("🤖 SISTEMA EXPERTO - RECOMENDADOR DE ARQUITECTURA")
        lineas.append("=" * 70)
        
        # Análisis de requerimientos
        lineas.append("\n🔍 ANÁLISIS DE REQUERIMIENTOS:")
        lineas.append("-" * 50)
        for clave, valor in respuestas.items():
            nombre = clave.replace('_', ' ').title()
            lineas.append(f"   • {nombre}: {valor}")
        
        # Confianza
        confianza = recomendacion.get('confianza', 0)
        barra = "█" * (confianza // 10) + "░" * (10 - confianza // 10)
        lineas.append(f"\n📊 NIVEL DE CONFIANZA: {confianza}% [{barra}]")
        
        # Combo sugerido
        if recomendacion.get('combo_sugerido'):
            lineas.append(f"\n🎯 COMBO SUGERIDO: {recomendacion['combo_sugerido']}")
        
        # Recomendación principal
        lineas.append("\n" + "=" * 70)
        lineas.append("✅ RECOMENDACIÓN (BEST CHOICE)")
        lineas.append("=" * 70)
        
        lineas.append(f"\n🚀 BACKEND: {recomendacion.get('backend', 'N/A')}")
        lineas.append(f"🎨 FRONTEND: {recomendacion.get('frontend', 'N/A')}")
        lineas.append(f"💾 BASE DE DATOS: {recomendacion.get('bd', 'N/A')}")
        lineas.append(f"☁️ DEPLOY: {recomendacion.get('deploy', 'N/A')}")
        
        lineas.append(f"\n📝 JUSTIFICACIÓN:")
        lineas.append(f"   {recomendacion.get('justificacion', '')}")
        
        # Alternativas consideradas (tabla)
        if recomendacion.get('alternativas'):
            lineas.append("\n📊 ALTERNATIVAS CONSIDERADAS:")
            lineas.append("-" * 50)
            for alt in recomendacion['alternativas']:
                lineas.append(f"   • {alt['stack']}")
                lineas.append(f"     ❌ Motivo de descarte: {alt['motivo_descarte']}")
        
        # Conflictos detectados
        if conflictos:
            lineas.append("\n⚠️ RIESGOS Y TRADE-OFFS DETECTADOS:")
            lineas.append("-" * 50)
            for conf in conflictos:
                lineas.append(f"   🔴 {conf['tipo']} (Severidad: {conf['severidad']})")
                lineas.append(f"      {conf['descripcion']}")
                lineas.append(f"      💡 Mitigación: {conf['recomendacion']}")
        
        # Casos CBR
        if casos_similares:
            lineas.append("\n🧠 RAZONAMIENTO BASADO EN CASOS (CBR):")
            lineas.append("-" * 50)
            for caso, sim in casos_similares:
                lineas.append(f"   • Caso #{caso['id']} (similitud: {sim:.0%})")
                lineas.append(f"     Stack usado: {caso['recomendacion']['backend']}")
        
        if alertas_cbr:
            lineas.append(f"\n   📌 {alertas_cbr}")
        
        # Estimación de costos
        lineas.append("\n💰 ESTIMACIÓN DE COSTOS (infraestructura):")
        lineas.append("-" * 50)
        costos = self._estimar_costos(respuestas, recomendacion)
        for concepto, rango in costos.items():
            lineas.append(f"   • {concepto}: {rango}")
        
        # Ruta de escalado
        lineas.append("\n🗺️ RUTA DE ESCALADO FUTURO:")
        lineas.append("-" * 50)
        escalado = self._ruta_escalado(respuestas, recomendacion)
        for paso in escalado:
            lineas.append(f"   {paso}")
        
        # Seguridad
        if respuestas.get('seguridad') in ['Medio (login, datos personales)', 
                                            'Alto (financiero/salud → PCI-DSS, HIPAA, GDPR)']:
            lineas.append("\n🔐 SEGURIDAD Y COMPLIANCE:")
            lineas.append("-" * 50)
            lineas.extend(self._recomendaciones_seguridad(respuestas))
        
        # Estrategia de testing
        lineas.append("\n🧪 ESTRATEGIA DE TESTING SUGERIDA:")
        lineas.append("-" * 50)
        lineas.extend(self._estrategia_testing(respuestas))
        
        lineas.append("\n" + "=" * 70)
        
        return "\n".join(lineas)
    
    def _estimar_costos(self, respuestas, recomendacion):
        """Estima costos mensuales de infraestructura."""
        presupuesto = respuestas.get('presupuesto_infra', 'Bajo (<$50 USD)')
        
        costos_base = {
            "Bajo (<$50 USD)": {
                "Hosting frontend": "$0 - $20 (Vercel/Netlify free tier)",
                "Backend/API": "$0 - $25 (Render/Railway free tier o serverless)",
                "Base de datos": "$0 - $15 (MongoDB Atlas, Supabase, Neon free tier)",
                "Total estimado": "$0 - $50/mes"
            },
            "Medio ($50-200 USD)": {
                "Hosting frontend": "$0 - $20 (Vercel Pro o Netlify)",
                "Backend/API": "$25 - $100 (Render/Railway paid, AWS ECS)",
                "Base de datos": "$15 - $50 (PostgreSQL gestionado, MongoDB Atlas)",
                "CDN/Servicios": "$10 - $30 (Cloudflare, dominios, SSL)",
                "Total estimado": "$50 - $200/mes"
            },
            "Alto ($200+ USD)": {
                "Hosting frontend": "$20 - $50",
                "Backend/API": "$100 - $300 (Kubernetes, autoescalado)",
                "Base de datos": "$50 - $200 (RDS, ElastiCache)",
                "CDN/Servicios": "$30 - $100 (CloudFront, monitoreo)",
                "Total estimado": "$200 - $650+/mes"
            }
        }
        
        return costos_base.get(presupuesto, costos_base["Bajo (<$50 USD)"])
    
    def _ruta_escalado(self, respuestas, recomendacion):
        """Genera ruta de escalado futuro."""
        escalabilidad = respuestas.get('escalabilidad', '<100')
        
        if escalabilidad in ['100k+', '10k-100k']:
            return [
                "1. Fase actual: MVP con stack recomendado",
                "2. Al superar 1k usuarios: Añadir Redis para caché",
                "3. Al superar 10k usuarios: Migrar a contenedores (Docker + K8s)",
                "4. Al superar 100k usuarios: Considerar sharding de BD y CDN global",
                "5. Evaluar microservicios solo si la complejidad lo justifica"
            ]
        else:
            return [
                "1. Fase actual: Stack actual es suficiente",
                "2. Si crece a 1k+ usuarios: Añadir CDN y caché básico",
                "3. Si crece a 10k+ usuarios: Migrar a servicios gestionados escalables",
                "4. Monitorear métricas para decidir cuándo escalar"
            ]
    
    def _recomendaciones_seguridad(self, respuestas):
        """Recomendaciones de seguridad según nivel."""
        seguridad = respuestas.get('seguridad', 'Bajo (informativo)')
        
        if 'Alto' in seguridad:
            return [
                "   • Encriptación en tránsito (TLS 1.3) y en reposo (AES-256)",
                "   • Autenticación multifactor (MFA) obligatoria",
                "   • Auditoría de accesos y logs inmutables",
                "   • Compliance: PCI-DSS (si hay pagos), HIPAA (salud), GDPR/ley local",
                "   • Pentesting anual y análisis de vulnerabilidades continuo",
                "   • Principio de mínimo privilegio (RBAC)"
            ]
        else:
            return [
                "   • HTTPS obligatorio con certificados SSL/TLS",
                "   • Hashing de contraseñas con bcrypt o argon2",
                "   • Validación de inputs para prevenir inyección SQL/XSS",
                "   • Rate limiting en endpoints de autenticación",
                "   • Variables de entorno para secretos (nunca hardcodear)"
            ]
    
    def _estrategia_testing(self, respuestas):
        """Estrategia de testing según experiencia del equipo."""
        experiencia = respuestas.get('experiencia_general', 'Mixto')
        
        if experiencia == 'Junior':
            return [
                "   • Testing manual guiado por checklist (empezar simple)",
                "   • Pruebas unitarias básicas con Jest/Pytest (cobertura 30-50%)",
                "   • Testing de API con Postman/Thunder Client",
                "   • Migrar gradualmente a TDD cuando el equipo gane confianza"
            ]
        elif experiencia == 'Senior':
            return [
                "   • TDD desde el inicio (cobertura 80%+)",
                "   • Testing de integración con contenedores (Testcontainers)",
                "   • E2E con Playwright/Cypress en CI/CD",
                "   • Contract testing si hay microservicios",
                "   • Performance testing con k6 o Artillery"
            ]
        else:
            return [
                "   • Testing unitario con Jest/Pytest (cobertura 60-70%)",
                "   • Testing de integración para endpoints críticos",
                "   • E2E básico con Playwright para flujos principales",
                "   • CI/CD con GitHub Actions ejecutando tests automáticamente"
            ]