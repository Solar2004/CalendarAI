import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import pickle
from utils.logger import logger
from utils.helpers import get_app_directory
from .auth_server import start_success_page

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

class GoogleAuthManager:
    def __init__(self):
        self.credentials = None
        # Cambiar la ubicación del token a un directorio persistente
        self.token_dir = os.path.join(get_app_directory(), 'tokens')
        os.makedirs(self.token_dir, exist_ok=True)
        self.token_path = os.path.join(self.token_dir, 'google_token.pickle')
        self.credentials_path = 'credentials.json'
        self._load_credentials()

    def _load_credentials(self):
        """Load existing credentials if available"""
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    self.credentials = pickle.load(token)
                logger.info("Token cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando token: {str(e)}")
            # Si hay error al cargar, eliminar el token corrupto
            if os.path.exists(self.token_path):
                os.remove(self.token_path)

    def get_credentials(self) -> Credentials:
        """Get valid credentials, refreshing or creating new ones if necessary"""
        try:
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refrescando token expirado...")
                    try:
                        self.credentials.refresh(Request())
                        self._save_credentials()
                        logger.info("Token refrescado exitosamente")
                    except RefreshError:
                        logger.warning("Error al refrescar token, creando nuevo...")
                        self.credentials = self._create_new_credentials()
                else:
                    logger.info("Creando nuevas credenciales...")
                    self.credentials = self._create_new_credentials()

            return self.credentials
        except Exception as e:
            logger.error(f"Error en get_credentials: {str(e)}")
            raise

    def _create_new_credentials(self) -> Credentials:
        """Create new credentials via OAuth2 flow"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                "credentials.json not found. Please download it from Google Cloud Console"
            )

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                SCOPES
            )
            
            # Mostrar la URL de autorización en la consola
            credentials = flow.run_local_server(
                port=0,  # Puerto aleatorio
                authorization_prompt_message='Por favor, visita esta URL para autorizar la aplicación: {url}',
                success_message='¡Autorización completada! Puedes cerrar esta ventana.',
                open_browser=True
            )
            
            # Mostrar la URL de autorización en texto plano
            logger.info(f"Por favor, visita esta URL para autorizar la aplicación: {flow.authorization_url}")
            logger.info("¡Autorización completada! Puedes cerrar esta ventana.")
            
            # Iniciar la página de éxito
            start_success_page()
            
            # Guardar las nuevas credenciales
            self._save_credentials(credentials)
            logger.info("Nuevas credenciales creadas y guardadas")
            
            return credentials
        except Exception as e:
            logger.error(f"Error creando nuevas credenciales: {str(e)}")
            raise

    def _save_credentials(self, credentials=None):
        """Guarda las credenciales en el archivo pickle"""
        try:
            with open(self.token_path, 'wb') as token:
                pickle.dump(credentials or self.credentials, token)
            logger.info(f"Credenciales guardadas en {self.token_path}")
        except Exception as e:
            logger.error(f"Error guardando credenciales: {str(e)}")

    def clear_credentials(self):
        """Limpia las credenciales y elimina el token guardado"""
        try:
            # Eliminar el archivo de token si existe
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
                logger.info("Token eliminado exitosamente")
            
            # Limpiar credenciales en memoria
            self.credentials = None
            logger.info("Credenciales limpiadas exitosamente")
            
        except Exception as e:
            logger.error(f"Error limpiando credenciales: {str(e)}")
            raise

    def is_authenticated(self) -> bool:
        """Check if we have valid credentials"""
        return self.credentials and self.credentials.valid

    def get_user_info(self):
        """Obtiene la información del perfil del usuario"""
        try:
            if not self.credentials:
                return {}
            
            # Crear servicio de OAuth2
            from googleapiclient.discovery import build
            oauth2_service = build('oauth2', 'v2', credentials=self.credentials)
            
            # Obtener información del usuario
            user_info = oauth2_service.userinfo().get().execute()
            
            return {
                'name': user_info.get('name', ''),
                'email': user_info.get('email', ''),
                'picture': user_info.get('picture', ''),
                'id': user_info.get('id', '')
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo información del usuario: {str(e)}")
            return {} 