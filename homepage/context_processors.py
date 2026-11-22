from rooms.models import Room


def project_info(request):
    return {"site_name": "РемонтПлан", "rooms_count": Room.objects.count()}
