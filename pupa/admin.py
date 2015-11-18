from django.contrib import admin
from . import models


class ScrapeReportInline(admin.TabularInline):
    model = models.ScrapeReport
    readonly_fields = ('scraper', 'args', 'start_time', 'end_time',
                       'get_object_list')

    def has_add_permission(self, request):
        return False
    can_delete = False

    def get_object_list(self, obj):
        return '\n'.join('{} ({})'.format(o.object_type, o.count) for o in
                         obj.scraped_objects.all())


class ImportObjectsInline(admin.TabularInline):
    model = models.ImportObjects
    readonly_fields = ('object_type', 'insert_count', 'update_count',
                       'noop_count', 'start_time', 'end_time')

    def has_add_permission(self, request):
        return False
    can_delete = False


@admin.register(models.RunPlan)
class RunPlanAdmin(admin.ModelAdmin):
    actions = None

    readonly_fields = ('jurisdiction', 'success', 'start_time', 'end_time',
                       'exception', 'traceback')
    list_filter = ('jurisdiction__name', 'success')
    list_display = ('jurisdiction', 'success', 'start_time')
    inlines = [
        ScrapeReportInline,
        ImportObjectsInline,
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
