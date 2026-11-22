from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods, require_POST

from rooms.models import Room
from .forms import EstimateFilterForm, EstimateForm
from .models import Estimate, Material, User


@require_http_methods(["GET", "POST"])
def estimate_create(request):
    form = EstimateForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            estimate = form.save()
        messages.success(request, "Смета создана.")
        return redirect("estimates:estimate_detail", estimate_id=estimate.pk)
    return render(request, "estimates/estimate_form.html", {"form": form})


@require_http_methods(["GET", "POST"])
def estimate_edit(request, estimate_id):
    estimate = get_object_or_404(Estimate, pk=estimate_id)
    form = EstimateForm(request.POST if request.method == "POST" else None,
                        instance=estimate)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, "Смета обновлена.")
        return redirect("estimates:estimate_detail", estimate_id=estimate.pk)
    return render(request, "estimates/estimate_form.html", {
        "form": form, "estimate": estimate,
    })


@require_POST
def estimate_cancel(request, estimate_id):
    estimate = get_object_or_404(Estimate, pk=estimate_id)
    Estimate.objects.filter(pk=estimate.pk).update(status=Estimate.Status.CANCELLED)
    messages.success(request, "Смета отменена. Данные и состав материалов сохранены.")
    return redirect("estimates:estimate_detail", estimate_id=estimate.pk)


def estimates_list(request):
    form = EstimateFilterForm(request.GET)
    estimates = Estimate.objects.all()
    if form.is_valid():
        data = form.cleaned_data
        if data["date"]:
            estimates = estimates.for_date(data["date"])
        status_methods = {
            Estimate.Status.ACTIVE: "active", Estimate.Status.CANCELLED: "cancelled",
            Estimate.Status.COMPLETED: "completed",
        }
        if data["status"] in status_methods:
            estimates = getattr(estimates, status_methods[data["status"]])()
        elif data["status"]:
            estimates = estimates.filter(status=data["status"])
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
        "id", "materials_cost", "works_cost", "total", "status", "estimate_date",
    ).annotate(room_name=F("room__name"), user_name=F("user__name"))
    page_obj = Paginator(estimates, 5).get_page(request.GET.get("page"))
    return render(request, "estimates/estimate_list.html", {
        "estimates": page_obj, "page_obj": page_obj, "form": form,
        "status_labels": dict(Estimate.Status.choices),
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
        count=Count("pk"),
        draft=Count("pk", filter=Q(status=Estimate.Status.DRAFT)),
        active=Count("pk", filter=Q(status=Estimate.Status.ACTIVE)),
        cancelled=Count("pk", filter=Q(status=Estimate.Status.CANCELLED)),
        completed=Count("pk", filter=Q(status=Estimate.Status.COMPLETED)),
        total_sum=Sum("total", default=0),
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
