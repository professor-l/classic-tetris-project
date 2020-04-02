def session_processor(request):
    if request.user.is_authenticated:
        user = request.user.website_user.user
    else:
        user = None

    return {
        "user": user,
    }
