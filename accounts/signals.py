from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import SessionLog

@receiver(user_logged_in)
def create_session_log(sender, request, user, **kwargs):
    """Crée un log de session lors de la connexion"""
    SessionLog.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        session_key=request.session.session_key
    )

@receiver(user_logged_out)
def end_session_log(sender, request, user, **kwargs):
    """Termine le log de session lors de la déconnexion"""
    if hasattr(request, 'session') and request.session.session_key:
        try:
            session_log = SessionLog.objects.filter(
                user=user,
                session_key=request.session.session_key,
                is_active=True
            ).latest('login_time')
            session_log.end_session()
        except SessionLog.DoesNotExist:
            pass

def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip