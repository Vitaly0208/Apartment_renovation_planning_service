from django.shortcuts import render


def index(request):
    """Главная страница."""
    return render(request, "homepage/index.html")


def page_not_found(request, exception):
    """Обработчик ошибки 404."""
    content = (
        "<h1 class=\"text-danger\">404 – страница не найдена</h1>\n"
        "<p>Проверьте адрес или вернитесь на главную.</p>\n"
        "<a href=\"/\" class=\"btn btn-primary\">На главную</a>\n"
    )
    from django.http import HttpResponse
    return HttpResponse(content, status=404)
