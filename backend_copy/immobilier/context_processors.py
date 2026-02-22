from .models import Proprietaire


def user_is_proprietaire(request):
    """Context processor to expose whether the current user is linked to a Proprietaire."""
    try:
        is_prop = request.user.is_authenticated and Proprietaire.objects.filter(user=request.user).exists()
    except Exception:
        is_prop = False
    return {"user_is_proprietaire": is_prop}
