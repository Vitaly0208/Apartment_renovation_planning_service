from django.http import HttpResponse


def page(title: str, content: str) -> str:
    """Единый HTML-каркас с Bootstrap 5.3."""
    css = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return (
        f"<!DOCTYPE html>\n<html lang=\"ru\">\n<head>\n"
        f"  <meta charset=\"UTF-8\">\n"
        f"  <meta name=\"viewport\" "
        f"content=\"width=device-width, initial-scale=1\">\n"
        f"  <title>{title}</title>\n"
        f"  <link rel=\"stylesheet\" href=\"{css}\">\n"
        f"</head>\n<body>\n"
        f"  <nav class=\"navbar navbar-expand-lg "
        f"navbar-dark bg-dark mb-4\">\n"
        f"    <div class=\"container\">\n"
        f"      <a class=\"navbar-brand\" href=\"/\">"
        f"РемонтПлан</a>\n"
        f"      <div class=\"navbar-nav\">\n"
        f"        <a class=\"nav-link\" href=\"/rooms/\">"
        f"Помещения</a>\n"
        f"        <a class=\"nav-link\" href=\"/estimates/\">"
        f"Сметы</a>\n"
        f"      </div>\n"
        f"    </div>\n"
        f"  </nav>\n"
        f"  <main class=\"container\">{content}</main>\n"
        f"</body>\n</html>"
    )


def index(request):
    """Главная страница."""
    content = (
        "<h1 class=\"display-4\">РемонтПлан</h1>\n"
        "<p class=\"lead\">Сервис планирования ремонта квартиры.</p>\n"
        "<a href=\"/rooms/\" class=\"btn btn-primary me-2\">"
        "Помещения</a>\n"
        "<a href=\"/estimates/\" class=\"btn btn-secondary\">"
        "Сметы</a>\n"
    )
    return HttpResponse(page("Главная", content))


def page_not_found(request, exception):
    """Обработчик ошибки 404."""
    content = (
        "<h1 class=\"text-danger\">404 – страница не найдена</h1>\n"
        "<p>Проверьте адрес или вернитесь на главную.</p>\n"
        "<a href=\"/\" class=\"btn btn-primary\">На главную</a>\n"
    )
    return HttpResponse(page("404", content), status=404)
