from django.shortcuts import render


def server_error(request):
    return render(None, '500.html', status=500)
