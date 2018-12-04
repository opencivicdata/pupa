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


@admin.register(models.SessionDataQualityReport)
class SessionDataQualityAdmin(admin.ModelAdmin):
    actions = None

    readonly_fields = ('legislative_session',
                       'bills_missing_actions',
                       'bills_missing_sponsors',
                       'bills_missing_versions',
                       'votes_missing_voters',
                       'votes_missing_bill',
                       'votes_missing_yes_count',
                       'votes_missing_no_count',
                       'votes_with_bad_counts',
                       'unmatched_sponsor_people',
                       'unmatched_sponsor_organizations',
                       'unmatched_voters',
                       )
    list_display = ('jurisdiction_name',
                    'legislative_session',
                    'bills_missing_actions',
                    'bills_missing_sponsors',
                    'bills_missing_versions',
                    'votes_missing_voters',
                    'votes_missing_bill',
                    'votes_missing_yes_count',
                    'votes_missing_no_count',
                    'votes_with_bad_counts',
                    )
    list_filter = ('legislative_session__jurisdiction__name',)

    def jurisdiction_name(self, obj):
        return obj.legislative_session.jurisdiction.name
