# Calendar Studio AI

Una aplicación de escritorio inteligente que ayuda a gestionar, analizar y optimizar tu calendario usando IA.

## Características

### Características Actuales
- **Predicciones de Eventos**: Analiza tendencias y predice eventos futuros
- **Optimización de Horarios**: Sugiere mejores distribuciones de eventos y reuniones
- **Sugerencias Inteligentes**: Recomienda mejoras en la gestión del tiempo
- **Chat con IA**: Asistente integrado para consultas y gestión
- **Panel de Desarrollo**: Herramientas para pruebas y configuración
- **Integración con Google Calendar**: Sincronización bidireccional

### Próximas Características
- **Smart Templates**: Plantillas inteligentes que aprenden de tus patrones de eventos
- **Calendar Analytics Dashboard**: Panel detallado de análisis de productividad
- **Cross-Calendar Conflict Resolution**: Resolución automática de conflictos
- **Voice Command Integration**: Control por voz para gestión de eventos
- **Time Zone Smart Scheduling**: Programación inteligente multi zona horaria

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/yourusername/calendar-studio-ai.git
cd calendar-studio-ai
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. Ejecutar la aplicación:
```bash
python src/main.py
```

## Configuración

1. Obtener credenciales de Google Calendar API:
   - Ir a Google Cloud Console
   - Crear un proyecto
   - Habilitar Calendar API
   - Crear credenciales OAuth
   - Descargar client_secrets.json

2. Configurar DeepSeek API:
   - Obtener API key de OpenRouter
   - Agregar a .env

## Uso

1. **Autenticación**:
   - Iniciar sesión con Google
   - Autorizar acceso al calendario

2. **Funciones Principales**:
   - Predicciones: Análisis predictivo de eventos
   - Optimización: Mejora de distribución horaria
   - Sugerencias: Recomendaciones de gestión

3. **Panel de Desarrollo**:
   - Acceder desde menú Tools
   - Configurar modo de API
   - Simular respuestas

## Desarrollo

### Contexto de Botones

1. **Predicciones**:
   - Analiza datos históricos y tendencias
   - Predice eventos futuros y su impacto
   - Genera resúmenes mensuales

2. **Optimizar**:
   - Analiza patrones de programación
   - Detecta conflictos y sobrecargas
   - Sugiere reorganización eficiente
   - Considera preferencias personales
   - Optimiza duración de reuniones

3. **Sugerir**:
   - Recomienda mejores prácticas
   - Identifica hábitos problemáticos
   - Sugiere espacios para descanso
   - Propone bloques de concentración
   - Balancea trabajo/vida personal

### Plan de Desarrollo

1. **Fase 1 - Optimización** (En progreso):
   - [ ] Algoritmo de análisis de patrones
   - [ ] Detección de conflictos
   - [ ] Motor de sugerencias de reorganización
   - [ ] UI para visualización de cambios
   - [ ] Implementación de acciones en lote

2. **Fase 2 - Sugerencias** (Planificado):
   - [ ] Sistema de análisis de hábitos
   - [ ] Base de conocimiento de mejores prácticas
   - [ ] Algoritmo de recomendaciones
   - [ ] UI para gestión de sugerencias
   - [ ] Sistema de feedback y aprendizaje

## Contribuir

1. Fork el repositorio
2. Crear rama de feature
3. Commit cambios
4. Push a la rama
5. Crear Pull Request

## Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles. 