import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import pickle
from utils.logger import logger
from utils.helpers import get_app_directory

SCOPES = ['https://www.googleapis.com/auth/calendar']

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
            
            credentials = flow.run_local_server(
                port=0,  # Puerto aleatorio
                authorization_prompt_message='Por favor, visita esta URL para autorizar la aplicación: {url}',
                success_message='¡Autorización completada! Puedes cerrar esta ventana.',
                open_browser=True
            )
            
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

    def is_authenticated(self) -> bool:
        """Check if we have valid credentials"""
        return self.credentials and self.credentials.valid 