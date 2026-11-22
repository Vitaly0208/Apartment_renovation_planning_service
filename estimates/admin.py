from django.contrib import admin

from .models import Estimate, Material, User


class EstimateInline(admin.TabularInline):
    model = Estimate
    fields = ("room", "user", "estimate_date", "status", "total")
    readonly_fields = fields
    extra = 0
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("room", "user")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email")
    list_display_links = ("id", "name")
    search_fields = ("name", "phone", "email")
    ordering = ("name", "pk")
    list_per_page = 20
    inlines = (EstimateInline,)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "unit", "price", "coverage")
    list_display_links = ("id", "name")
    list_editable = ("price",)
    search_fields = ("name",)
    list_filter = ("unit",)
    ordering = ("name", "pk")
    list_per_page = 20


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "user", "estimate_date", "status", "total")
    list_display_links = ("id",)
    list_filter = ("status", "room", "user", "estimate_date")
    search_fields = ("room__name", "user__name", "user__email")
    ordering = ("-estimate_date", "-pk")
    list_per_page = 20
    list_select_related = ("room", "user")
    autocomplete_fields = ("room", "user")
    filter_horizontal = ("materials",)
    readonly_fields = ("total",)
    fields = ("room", "user", "estimate_date", "status", "materials",
              "materials_cost", "works_cost", "total")

    def get_form(self, request, obj=None, **kwargs):
        from .forms import EstimateAdminForm
        kwargs["form"] = EstimateAdminForm
        return super().get_form(request, obj, **kwargs)


admin.site.site_header = "РемонтПлан — управление"
admin.site.site_title = "РемонтПлан"
admin.site.index_title = "Управление данными ремонта"
