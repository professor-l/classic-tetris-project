def session_processor(request):
    if request.path.startswith("/admin"):
        return {}

    if request.user.is_authenticated and hasattr(request.user, "website_user"):
        current_user = request.user.website_user.user
    else:
        current_user = None

    return {
        "auth_user": request.user,
        "current_user": current_user,
    }
