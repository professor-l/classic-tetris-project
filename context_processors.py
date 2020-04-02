def session_processor(request):
    if request.path.startswith("/admin"):
        return {}

    if request.user.is_authenticated and hasattr(request.user, "website_user"):
        user = request.user.website_user.user
    else:
        user = None

    return {
        "user": user,
    }
