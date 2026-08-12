from django.conf import settings
# API_BASE='/api/v1'
API_BASE = settings.API_BASE


def api_url(path):
    """Build a versioned API URL from the shared base."""
    return f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"
