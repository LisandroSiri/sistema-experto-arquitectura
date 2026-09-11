"""
Motor de inferencia basado en Experta.
Implementa el ciclo de razonamiento hacia adelante (forward chaining).
"""
from experta import KnowledgeEngine, Rule, MATCH, TEST, AS, L, NOT, OR, AND
from .facts import RespuestaUsuario, PerfilProyecto, RecomendacionStack, ConflictoDetectado
import json
import os

class MotorArquitectura(KnowledgeEngine):
    """
    Motor de reglas que:
    1. Recibe las respuestas del usuario como hechos
    2. Aplica reglas de inferencia
    3. Genera recomendaciones, detecta conflictos y calcula confianza
    """
    
    def __init__(self):
        super().__init__()
        self.recomendaciones = []
        self.conflictos = []
        self.alertas = []
        self.explicaciones_descarte = []
        self._cargar_stacks()
    
    def _cargar_stacks(self):
        """Carga el catálogo de tecnologías desde JSON."""
        ruta = os.path.join(os.path.dirname(__file__), '..', 'data', 'stacks.json')
        with open(ruta, 'r', encoding='utf-8') as f:
            self.stacks = json.load(f)
    
    # ============================================================
    # REGLAS DE DETECCIÓN DE CONFLICTOS
    # ============================================================
    
    @Rule(
        RespuestaUsuario(clave='presupuesto_infra', valor='Bajo (<$50 USD)'),
        RespuestaUsuario(clave='escalabilidad', valor=L('100k+') | L('10k-100k')),
        salience=100  # Alta prioridad: los conflictos se detectan primero
    )
    def conflicto_presupuesto_escalabilidad(self):
        """Detecta conflicto entre presupuesto bajo y alta escalabilidad."""
        self.conflictos.append({
            "tipo": "Presupuesto vs. Escalabilidad",
            "descripcion": "Presupuesto bajo con requerimiento de alta escalabilidad. "
                          "No es imposible, pero requerirá arquitecturas serverless o "
                          "servicios gestionados con costo variable. Considera que el "
                          "costo puede escalar rápidamente con el uso.",
            "severidad": "Alta",
            "recomendacion": "Evaluar servicios serverless (Firebase, Supabase) o "
                           "VPS con autoescalado manual. Revisar pricing de cloud."
        })
        self.declare(ConflictoDetectado(
            tipo='presupuesto_escalabilidad',
            severidad='alta'
        ))
    
    @Rule(
        RespuestaUsuario(clave='experiencia_general', valor='Junior'),
        RespuestaUsuario(clave='plazo', valor=L('Inmediato (días)') | L('Corto (semanas)')),
        salience=100
    )
    def conflicto_junior_plazo(self):
        """Detecta conflicto entre equipo junior y plazo corto."""
        self.conflictos.append({
            "tipo": "Experiencia vs. Plazo",
            "descripcion": "Equipo junior con plazo muy ajustado. La curva de aprendizaje "
                          "puede consumir el tiempo disponible.",
            "severidad": "Alta",
            "recomendacion": "Priorizar stacks con baja curva de aprendizaje y alta "
                           "documentación. Considerar contratar un senior temporalmente."
        })
        self.declare(ConflictoDetectado(
            tipo='junior_plazo',
            severidad='alta'
        ))
    
    @Rule(
        RespuestaUsuario(clave='tiempo_real', valor='Sí (websockets, colaboración en vivo)'),
        RespuestaUsuario(clave='presupuesto_infra', valor='Bajo (<$50 USD)')
    )
    def conflicto_tiempo_real_presupuesto(self):
        """Tiempo real con presupuesto bajo."""
        self.conflictos.append({
            "tipo": "Tiempo Real vs. Presupuesto",
            "descripcion": "Tiempo real (websockets) con presupuesto bajo puede requerir "
                          "servicios gestionados que tienen costo por conexión.",
            "severidad": "Media",
            "recomendacion": "Considerar Supabase Realtime (capa gratuita generosa) o "
                           "Firebase Realtime Database."
        })
    
    # ============================================================
    # REGLAS DE RECOMENDACIÓN - WEB
    # ============================================================

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Web'),
        RespuestaUsuario(clave='naturaleza', valor='Contenido/publishing (blog, landing, e-commerce)'),
        RespuestaUsuario(clave='seo_ssr', valor=L('Sí, crítico') | L('Sí, deseable')),
        salience=60
    )
    def web_contenido_seo(self):
        print("Regla web_contenido_seo activada")
        self._agregar_recomendacion(
            backend="Next.js API Routes (fullstack)",
            frontend="Next.js + Tailwind CSS",
            bd="PostgreSQL + Prisma (o SQLite para MVP)",
            deploy="Vercel + Neon/Supabase (BD)",
            justificacion="Next.js cubre SEO con SSR/SSG. API Routes evitan backend "
                         "separado. Vercel deploy gratuito. Ideal para contenido.",
            alternativas=[
                {"stack": "Astro + React islands", "motivo_descarte": "Menos flexible para CRUD"},
                {"stack": "Remix", "motivo_descarte": "Menor comunidad"}
            ],
            combo_sugerido="T3 Stack", confianza=90
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Web'),
        RespuestaUsuario(clave='naturaleza', valor=L('CRUD/gestión de datos') | L('Integración de sistemas')),
        RespuestaUsuario(clave='tamano_equipo', valor=L('1 persona') | L('2-5 personas')),
        salience=55
    )
    def web_crud_pequeno(self):
        print("Regla web_crud_pequeno activada")
        self._agregar_recomendacion(
            backend="Node.js + Express + TypeScript",
            frontend="React + Vite",
            bd="PostgreSQL + Prisma",
            deploy="Vercel + Railway/Render + Neon",
            justificacion="Stack versátil con gran comunidad. TypeScript en ambos "
                         "lados. Prisma simplifica la BD.",
            alternativas=[
                {"stack": "MERN (MongoDB)", "motivo_descarte": "Menos consistencia relacional"},
                {"stack": "Next.js fullstack", "motivo_descarte": "Si no necesitás SEO"}
            ],
            combo_sugerido="PERN", confianza=85
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Web'),
        RespuestaUsuario(clave='seguridad', valor='Alto (financiero/salud → PCI-DSS, HIPAA, GDPR)'),
        RespuestaUsuario(clave='tamano_equipo', valor=L('6-15 personas') | L('15+ personas')),
        salience=60
    )
    def web_empresarial(self):
        self._agregar_recomendacion(
            backend="Java + Spring Boot",
            frontend="React + TypeScript",
            bd="PostgreSQL + Redis",
            deploy="AWS ECS/EKS + RDS + ElastiCache",
            justificacion="Spring Boot: estándar empresarial con seguridad robusta "
                         "(Spring Security) y compliance (PCI-DSS, HIPAA).",
            alternativas=[
                {"stack": ".NET Core", "motivo_descarte": "Menor adopción en el equipo"},
                {"stack": "NestJS", "motivo_descarte": "Menos maduro para compliance estricto"}
            ],
            combo_sugerido=None, confianza=92
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Web'),
        RespuestaUsuario(clave='tiempo_real', valor='Sí (websockets, colaboración en vivo)'),
        salience=58
    )
    def web_tiempo_real(self):
        self._agregar_recomendacion(
            backend="Next.js + Supabase Realtime",
            frontend="Next.js + React",
            bd="Supabase (PostgreSQL + Realtime)",
            deploy="Vercel + Supabase",
            justificacion="Supabase Realtime ofrece websockets gestionados con capa "
                         "gratuita. Next.js cubre frontend y API.",
            alternativas=[
                {"stack": "Node + Socket.io + Redis", "motivo_descarte": "Más infra que administrar"},
                {"stack": "Firebase Realtime DB", "motivo_descarte": "Vendor lock-in"}
            ],
            combo_sugerido=None, confianza=87
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Web'),
        salience=5
    )
    def web_fallback(self):
        print("Regla web_fallback activada")
        if not self.recomendaciones:
            self._agregar_recomendacion(
                backend="Node.js + Express + TypeScript",
                frontend="React + Vite",
                bd="PostgreSQL + Prisma",
                deploy="Vercel + Railway/Render + Neon",
                justificacion="Stack versátil y con gran comunidad. Cubre la mayoría "
                             "de casos web sin requerimientos extremos.",
                alternativas=[
                    {"stack": "Next.js fullstack", "motivo_descarte": "Si no necesitás SEO"},
                    {"stack": "Python + FastAPI", "motivo_descarte": "Si preferís Python"}
                ],
                combo_sugerido="PERN", confianza=70
            )

    # ============================================================
    # REGLAS DE RECOMENDACIÓN - MÓVIL
    # ============================================================

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Móvil (nativa/híbrida)'),
        RespuestaUsuario(clave='tecnologias_dominadas', valor=MATCH.t),
        TEST(lambda t: 'JavaScript/TypeScript' in t),
        RespuestaUsuario(clave='multiplataforma', valor='Sí (React Native, Flutter, etc.)'),
        salience=55
    )
    def movil_react_native(self):
        self._agregar_recomendacion(
            backend="Node.js + Express (o Firebase)",
            frontend="React Native + Expo",
            bd="PostgreSQL o Firebase Firestore",
            deploy="Expo EAS + App Stores",
            justificacion="Aprovecha conocimiento JS del equipo. Expo simplifica "
                         "desarrollo y despliegue móvil.",
            alternativas=[
                {"stack": "Flutter", "motivo_descarte": "Requiere aprender Dart"}
            ],
            combo_sugerido=None, confianza=85
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Móvil (nativa/híbrida)'),
        RespuestaUsuario(clave='presupuesto_infra', valor='Bajo (<$50 USD)'),
        salience=50
    )
    def movil_flutter_firebase(self):
        self._agregar_recomendacion(
            backend="Firebase (Auth, Firestore, Cloud Functions)",
            frontend="Flutter (Dart)",
            bd="Firebase Firestore",
            deploy="Firebase Hosting + App Stores",
            justificacion="Flutter compila nativo iOS/Android con una base de código. "
                         "Firebase elimina backend propio con capa gratuita.",
            alternativas=[
                {"stack": "React Native + Expo", "motivo_descarte": "Rendimiento ligeramente inferior"},
                {"stack": "Kotlin Multiplatform", "motivo_descarte": "Curva alta, ecosistema inmaduro"}
            ],
            combo_sugerido=None, confianza=87
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Móvil (nativa/híbrida)'),
        salience=5
    )
    def movil_fallback(self):
        if not self.recomendaciones:
            self._agregar_recomendacion(
                backend="Node.js + Express + TypeScript",
                frontend="React Native + Expo",
                bd="PostgreSQL + Prisma",
                deploy="Expo EAS + Railway + Neon",
                justificacion="Stack móvil estándar con JS/TS. Buen balance entre "
                             "rendimiento y velocidad de desarrollo.",
                alternativas=[
                    {"stack": "Flutter + Firebase", "motivo_descarte": "Si el equipo prefiere Dart"}
                ],
                combo_sugerido=None, confianza=75
            )

    # ============================================================
    # REGLAS DE RECOMENDACIÓN - API / MICROSERVICIO
    # ============================================================

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor=L('API/Backend puro') | L('Microservicio')),
        RespuestaUsuario(clave='rendimiento', valor='Alto (<100ms)'),
        RespuestaUsuario(clave='escalabilidad', valor=L('10k-100k') | L('100k+')),
        salience=60
    )
    def api_alto_rendimiento(self):
        self._agregar_recomendacion(
            backend="Go + Gin",
            frontend="No aplica (solo API)",
            bd="PostgreSQL + Redis (caché)",
            deploy="Docker + Kubernetes (AWS EKS o GKE)",
            justificacion="Go: rendimiento excepcional y concurrencia nativa. "
                         "Redis reduce latencia. K8s maneja escalado.",
            alternativas=[
                {"stack": "Java Spring Boot", "motivo_descarte": "Mayor consumo de recursos"},
                {"stack": "Rust + Actix", "motivo_descarte": "Curva muy alta"}
            ],
            combo_sugerido=None, confianza=90
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor=L('API/Backend puro') | L('Microservicio')),
        RespuestaUsuario(clave='naturaleza', valor=L('IA/ML') | L('Procesamiento/analítica de datos')),
        salience=60
    )
    def api_ia_ml(self):
        self._agregar_recomendacion(
            backend="Python + FastAPI",
            frontend="Streamlit o no aplica",
            bd="PostgreSQL + Redis (caché)",
            deploy="Docker + Railway/Render o AWS ECS",
            justificacion="FastAPI: async nativo, ideal para IA/ML. Ecosistema Python "
                         "(pandas, scikit-learn, PyTorch) integrado directamente.",
            alternativas=[
                {"stack": "Django REST + DRF", "motivo_descarte": "Más pesado para solo API"},
                {"stack": "Flask", "motivo_descarte": "Menos features async"}
            ],
            combo_sugerido=None, confianza=90
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor=L('API/Backend puro') | L('Microservicio')),
        RespuestaUsuario(clave='seguridad', valor='Alto (financiero/salud → PCI-DSS, HIPAA, GDPR)'),
        salience=58
    )
    def api_empresarial(self):
        self._agregar_recomendacion(
            backend="Java + Spring Boot",
            frontend="No aplica (solo API)",
            bd="PostgreSQL + Redis",
            deploy="AWS ECS/EKS + RDS",
            justificacion="Spring Boot: seguridad robusta y compliance para APIs "
                         "empresariales críticas.",
            alternativas=[
                {"stack": ".NET Core", "motivo_descarte": "Menor adopción en el equipo"},
                {"stack": "Go + Gin + OAuth2", "motivo_descarte": "Menos 'baterías incluidas'"}
            ],
            combo_sugerido=None, confianza=90
        )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor=L('API/Backend puro') | L('Microservicio')),
        salience=5
    )
    def api_fallback(self):
        if not self.recomendaciones:
            self._agregar_recomendacion(
                backend="Node.js + Express + TypeScript",
                frontend="No aplica (solo API)",
                bd="PostgreSQL + Prisma",
                deploy="Railway/Render + Neon",
                justificacion="Stack API estándar con buen ecosistema y comunidad. "
                             "TypeScript añade seguridad de tipos.",
                alternativas=[
                    {"stack": "Python + FastAPI", "motivo_descarte": "Si preferís Python"},
                    {"stack": "Go + Gin", "motivo_descarte": "Si necesitás máximo rendimiento"}
                ],
                combo_sugerido=None, confianza=75
            )

    # ============================================================
    # REGLAS DE RECOMENDACIÓN - OTROS TIPOS (fallbacks)
    # ============================================================

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Escritorio'),
        salience=5
    )
    def escritorio_fallback(self):
        if not self.recomendaciones:
            self._agregar_recomendacion(
                backend="Tauri (Rust) o Electron (Node)",
                frontend="React + Vite",
                bd="SQLite (local)",
                deploy="Instaladores nativos (.exe/.dmg/.deb)",
                justificacion="Tauri: binarios pequeños y rápidos. Electron: ecosistema "
                             "JS más amplio. SQLite no requiere servidor.",
                alternativas=[
                    {"stack": "Python + PyQt", "motivo_descarte": "Si preferís Python"},
                    {"stack": ".NET MAUI", "motivo_descarte": "Si el equipo usa C#"}
                ],
                combo_sugerido=None, confianza=80
            )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='CLI/herramienta interna'),
        salience=5
    )
    def cli_fallback(self):
        if not self.recomendaciones:
            self._agregar_recomendacion(
                backend="Python + Click/Typer",
                frontend="No aplica (terminal)",
                bd="SQLite o JSON local",
                deploy="PyPI o binario con PyInstaller",
                justificacion="Python ofrece el desarrollo más rápido de CLIs. "
                             "Click y Typer simplifican el parsing de argumentos.",
                alternativas=[
                    {"stack": "Go + Cobra", "motivo_descarte": "Si necesitás binario único"},
                    {"stack": "Node + Commander", "motivo_descarte": "Si el equipo usa JS"}
                ],
                combo_sugerido=None, confianza=85
            )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor='Bot/automatización'),
        salience=5
    )
    def bot_fallback(self):
        if not self.recomendaciones:
            self._agregar_recomendacion(
                backend="Python + Playwright/Selenium",
                frontend="No aplica",
                bd="SQLite o CSV",
                deploy="VPS (DigitalOcean) o serverless (AWS Lambda)",
                justificacion="Python tiene el mejor ecosistema para automatización "
                             "y scraping. Playwright es moderno y rápido.",
                alternativas=[
                    {"stack": "Node + Puppeteer", "motivo_descarte": "Si el equipo usa JS"},
                    {"stack": "Zapier/Make", "motivo_descarte": "Si no requiere código"}
                ],
                combo_sugerido=None, confianza=88
            )

    @Rule(
        RespuestaUsuario(clave='tipo_proyecto', valor=L('Extensión de navegador') | L('IoT')),
        salience=5
    )
    def otros_fallback(self):
        if not self.recomendaciones:
            self._agregar_recomendacion(
                backend="JavaScript + Manifest V3 (extensión) / MicroPython o C++ (IoT)",
                frontend="React + Vite",
                bd="chrome.storage (extensión) / SQLite o InfluxDB (IoT)",
                deploy="Chrome Web Store / Firmware en dispositivo",
                justificacion="Extensiones: JS es obligatorio. IoT: MicroPython para "
                             "prototipos, C++ para producción en microcontroladores.",
                alternativas=[
                    {"stack": "ESP32 + MQTT + Node-RED", "motivo_descarte": "Para IoT más complejo"}
                ],
                combo_sugerido=None, confianza=75
            )

    def _agregar_recomendacion(self, backend, frontend, bd, deploy, justificacion,
                                alternativas, combo_sugerido, confianza):
        print(f">>> [DEBUG] _agregar_recomendacion llamado con backend={backend}")
        """Método helper para agregar recomendaciones de forma consistente."""
        confianza_ajustada = self._calcular_confianza(confianza)
        
        self.recomendaciones.append({
            "backend": backend,
            "frontend": frontend,
            "bd": bd,
            "deploy": deploy,
            "justificacion": justificacion,
            "alternativas": alternativas,
            "combo_sugerido": combo_sugerido,
            "confianza": confianza_ajustada
        })


    
    def _calcular_confianza(self, base):
        """
        Ajusta la confianza según la claridad de las respuestas.
        Si hay conflictos, reduce la confianza.
        """
        penalizacion = len(self.conflictos) * 10
        return max(50, min(99, base - penalizacion))
    
    def obtener_respuestas_dict(self):
        """Convierte los hechos de respuesta en un diccionario plano."""
        respuestas = {}
        for hecho in self.facts.values():
            if isinstance(hecho, RespuestaUsuario):
                respuestas[hecho['clave']] = hecho['valor']
        return respuestas