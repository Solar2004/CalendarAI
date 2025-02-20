# PyQt Google Calendar AI App

## Descripción General

Esta aplicación en Python usa **PyQt** para la interfaz gráfica y la API de **Google Calendar** para administrar eventos en un calendario de Google. También incorpora una IA basada en **DeepSeek (OpenRouter)** para asistir en la gestión de eventos.

## Características Principales

### 1. **Autenticación con Google**

- Los usuarios inician sesión con Google.
- Al otorgar permisos, la aplicación obtiene acceso al calendario del usuario.

### 2. **Gestión de Eventos**

- Visualización de eventos del **Google Calendar** en la aplicación con opciones de filtrado.
- Creación, edición y eliminación de eventos.
- Soporte para **repetición de eventos** (diaria, semanal, personalizada).
- Creación automática de eventos a partir de texto con IA.
- **Historial de acciones** almacenado en una base de datos SQL.
- **Opción de revertir acciones** como la creación o eliminación de eventos.

### 3. **Asistente de IA**

- Procesa comandos del usuario para gestionar eventos.
- Genera estructuras **JSON** para la API de Google Calendar.
- Ejemplo:
  - Entrada: *"Crear un evento 'Lavar los dientes' todos los viernes a las 9PM hasta las 12PM con esta descripción: 'Higiene bucal nocturna'."*
  - Salida: JSON estructurado con la información del evento.
- Interfaz con una **ventana de contexto** donde se pueden almacenar mini documentos con información relevante.
- Una segunda ventana de contexto describe el rol de la IA como servicial y asistente de planificación.

### 4. **Interfaz Gráfica con PyQt**

- **Dark Mode** integrado para comodidad visual.
- Diseño **minimalista** con enfoque en la productividad.
- Visualización de calendario en diferentes formatos (diario, semanal, mensual) con opciones de filtrado.
- Panel lateral para la IA con historial de interacciones y opciones de edición de contexto.
- **Botón para acceder al historial de eventos** almacenados en SQL.

## Flujo de Uso

1. **Inicio de Sesión**: El usuario accede con su cuenta de Google y otorga permisos.
2. **Visualización del Calendario**: Se muestran los eventos actuales con posibilidad de filtrado.
3. **Interacción con la IA**:
   - Se le puede pedir a la IA que cree eventos basados en texto natural.
   - La IA genera el JSON correspondiente y lo envía a Google Calendar.
4. **Gestión Manual**:
   - El usuario puede modificar eventos directamente en la UI.
   - Soporte para edición avanzada de eventos (repeticiones, duración, descripciones).
   - Posibilidad de **revertir cambios** en los eventos usando el historial.
5. **Configuraciones**:
   - Modificar información de la IA en su ventana de contexto.
   - Cambiar preferencias visuales (modo oscuro, tamaño de fuente, etc.).

## Tecnologías Utilizadas

- **Python** (backend principal)
- **PyQt** (interfaz gráfica)
- **Google Calendar API** (gestión de eventos)
- **DeepSeek AI (OpenRouter)** (asistente inteligente)
- **OAuth 2.0** (autenticación con Google)
- **SQLite / PostgreSQL** (almacenamiento del historial de acciones)

## Consideraciones Técnicas

- Implementación de **OAuth 2.0** para autenticación segura.
- Manejo de credenciales de Google Calendar con **API keys y OAuth tokens**.
- Integración fluida entre PyQt y la IA con **procesos asincrónicos**.
- Base de datos para almacenar y revertir acciones realizadas en el calendario.
- Posibilidad de expansión con más funciones de productividad en futuras versiones.

## Estructura de Carpetas

```plaintext
calendar_app/
├── src/
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Configuraciones globales
│   │   └── constants.py        # Constantes de la aplicación
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # Gestión de base de datos
│   │   ├── google_calendar.py  # Integración con Google Calendar
│   │   └── ai_assistant.py     # Lógica del asistente IA
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Ventana principal
│   │   ├── calendar_view.py    # Vista del calendario
│   │   ├── ai_chat.py         # Panel de chat con IA
│   │   └── components/        # Componentes UI reutilizables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── event.py           # Modelo de eventos
│   │   └── action.py          # Modelo de acciones
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Sistema de logging
│       └── helpers.py         # Funciones auxiliares
├── tests/                     # Tests unitarios y de integración
├── resources/                 # Recursos estáticos (iconos, estilos)
├── docs/                      # Documentación
└── data/                      # Datos locales y caché
```

## Esquema de Base de Datos

### Tabla: events
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_event_id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    recurrence_rule TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

### Tabla: actions
```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,  -- CREATE, UPDATE, DELETE
    event_id INTEGER,
    previous_state JSON,        -- Estado anterior del evento
    new_state JSON,            -- Nuevo estado del evento
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT NOT NULL,     -- ID del usuario de Google
    is_reverted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (event_id) REFERENCES events(id)
);
```

### Tabla: ai_context
```sql
CREATE TABLE ai_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Tabla: ai_chat_history
```sql
CREATE TABLE ai_chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_id INTEGER,
    action_taken TEXT,         -- Acción resultante (si hubo)
    FOREIGN KEY (context_id) REFERENCES ai_context(id)
);
```

### Tabla: user_preferences
```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    theme_mode TEXT DEFAULT 'dark',
    calendar_view TEXT DEFAULT 'month',
    font_size INTEGER DEFAULT 12,
    ai_context_enabled BOOLEAN DEFAULT TRUE,
    last_sync_timestamp TIMESTAMP
);
```

### Índices
```sql
CREATE INDEX idx_events_google_id ON events(google_event_id);
CREATE INDEX idx_events_dates ON events(start_datetime, end_datetime);
CREATE INDEX idx_actions_event ON actions(event_id);
CREATE INDEX idx_actions_timestamp ON actions(timestamp);
CREATE INDEX idx_chat_history_timestamp ON ai_chat_history(timestamp);
```
```
