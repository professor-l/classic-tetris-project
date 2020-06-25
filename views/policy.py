from django.shortcuts import render

def cookies(request):
    return render(request, "policy/cookies.html")
