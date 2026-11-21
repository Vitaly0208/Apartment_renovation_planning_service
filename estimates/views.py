from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.shortcuts import get_object_or_404, render

from rooms.models import Room
from .forms import EstimateFilterForm
from .models import Estimate, Material, User


def estimates_list(request):
    form = EstimateFilterForm(request.GET)
    estimates = Estimate.objects.all()
    if form.is_valid():
        data = form.cleaned_data
        if data["room"]:
            estimates = estimates.filter(room=data["room"])
        if data["user"]:
            estimates = estimates.filter(user=data["user"])
        if data["min_total"] is not None:
            estimates = estimates.filter(total__gte=data["min_total"])
        if data["max_total"] is not None:
            estimates = estimates.filter(total__lte=data["max_total"])
        if data["paid_only"]:
            estimates = estimates.exclude(total=0)
        if data["q"]:
            estimates = estimates.filter(
                Q(room__name__icontains=data["q"])
                | Q(user__name__icontains=data["q"])
                | Q(user__email__icontains=data["q"]))
        sort = {"id": "pk", "total": "total", "-total": "-total",
                "room": "room__name", "user": "user__name"}
        estimates = estimates.order_by(sort.get(data["sort"], "pk"), "pk")
    else:
        estimates = estimates.none()
    estimates = estimates.values(
        "id", "materials_cost", "works_cost", "total",
    ).annotate(room_name=F("room__name"), user_name=F("user__name"))
    page_obj = Paginator(estimates, 5).get_page(request.GET.get("page"))
    return render(request, "estimates/estimate_list.html", {
        "estimates": page_obj, "page_obj": page_obj, "form": form,
    })


def estimate_detail(request, estimate_id):
    estimate = get_object_or_404(
        Estimate.objects.select_related("room", "user").prefetch_related("materials"),
        pk=estimate_id,
    )
    return render(request, "estimates/estimate_detail.html", {"estimate": estimate})


def statistics(request):
    stats = User.objects.annotate(
        user_name=F("name"), estimates_count=Count("estimates"),
        total_spent=Sum("estimates__total", default=0),
        avg_cost=Avg("estimates__total", default=0),
    ).order_by("-total_spent", "name", "pk")
    summary = Estimate.objects.aggregate(
        count=Count("pk"), total_sum=Sum("total", default=0),
        average=Avg("total", default=0), minimum=Min("total"), maximum=Max("total"),
    )
    rooms = Room.objects.annotate(
        estimates_count=Count("estimates"),
        total_spent=Sum("estimates__total", default=0),
    ).order_by("-total_spent", "pk")
    materials = Material.objects.annotate(
        estimates_count=Count("estimates"),
    ).order_by("-estimates_count", "name", "pk")
    return render(request, "estimates/statistics.html", {
        "stats": stats, "summary": summary, "room_stats": rooms,
        "material_stats": materials,
    })
