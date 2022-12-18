from django.shortcuts import render


def csrf_failure(request, reason=''):
    template = 'includes/core/403csrf.html'
    return render(request, template)


def page_not_found(request, exception):
    template = 'includes/core/404.html'
    context = {
        'path': request.path
    }
    return render(request, template, context, status=404)


def permission_denied(request, exception):
    template = 'includes/core/403.html'
    return render(request, template, status=403)


def server_error(request):
    template = 'includes/core/500.html'
    return render(request, template, status=500)
