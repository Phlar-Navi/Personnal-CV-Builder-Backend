from django.utils import timezone
from django.conf import settings
from accounts.models import SessionLog

class SessionTrackingMiddleware:
    """
    Middleware pour tracker automatiquement la fin des sessions
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si l'utilisateur a une session active
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._update_last_activity(request)

        response = self.get_response(request)

        # Marquer les sessions inactives comme terminées
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._check_session_timeout(request)

        return response

    def _update_last_activity(self, request):
        """Met à jour la dernière activité de l'utilisateur"""
        # On pourrait ajouter un champ last_activity au modèle User
        # Pour l'instant, on se contente de vérifier la session
        pass

    def _check_session_timeout(self, request):
        """Vérifie si la session a expiré"""
        # Terminer automatiquement les sessions après une période d'inactivité
        timeout_minutes = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30)

        try:
            session_log = SessionLog.objects.filter(
                user=request.user,
                session_key=request.session.session_key,
                is_active=True
            ).latest('login_time')

            # Si la session est plus vieille que le timeout, la terminer
            if (timezone.now() - session_log.login_time).total_seconds() / 60 > timeout_minutes:
                session_log.end_session()

        except SessionLog.DoesNotExist:
            pass