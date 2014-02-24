from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy
from phillyleg.admin_views import MergeCouncilMembersView
from phillyleg.models import (
    CouncilMember, LegAction, LegFileAttachment, LegFile, LegFileMetaData,
    CouncilMemberAlias, CouncilMemberTenure, MetaData_Word, MetaData_Location,
    MetaData_Topic, CouncilDistrict, LegMinutes, LegVote, CouncilDistrictPlan)


class LegActionInline(admin.StackedInline):
    model = LegAction
    extra = 1

class LegFileAttachmentInline(admin.StackedInline):
    model = LegFileAttachment
    extra = 1

class LegFileAdmin(admin.ModelAdmin):
    inlines = [LegActionInline, LegFileAttachmentInline]
    readonly_fields = ['locations']

    def locations(self, instance):
        return ','.join(['<a href="%s">%s</a>' % (
            reverse("admin:phillyleg_metadata_location_change", args=(loc.id,)) , str(loc))
            for loc in instance.metadata.locations.all()])
    locations.allow_tags = True
    locations.short_description = 'Locations mentioned'

class LegMinutesAdmin(admin.ModelAdmin):
    inlines = [LegActionInline]

class LegFileInline (admin.TabularInline):
    model = LegFile
    fields = ['id', 'title']
    extra = 1

class LegFileWordInline(admin.TabularInline):
    model = LegFileMetaData.words.through
    extra = 1

class WordAdmin (admin.ModelAdmin):
    model = MetaData_Word
    inlines = [LegFileWordInline]

class LocationAdmin (admin.OSMGeoAdmin):
    model = MetaData_Location
    list_display = ['__unicode__', 'valid']
    search_fields = ['matched_text', 'address']
    readonly_fields = ['legfiles']

    def legfiles(self, instance):
        return ','.join(['<a href="%s">%s</a>' % (
            reverse("admin:phillyleg_legfile_change", args=(m.legfile.key,)) , str(m.legfile))
            for m in instance.references_in_legislation.all()])
    legfiles.allow_tags = True
    legfiles.short_description = 'References in legislation'

class CouncilDistrictInline(admin.TabularInline):
    model = CouncilDistrict
    extra = 0

class CouncilDistrictPlanAdmin (admin.OSMGeoAdmin):
    inlines = [CouncilDistrictInline]

class CouncilMemberTenureInline (admin.TabularInline):
    model = CouncilMemberTenure
    extra = 1

class CouncilMemberAliasInline (admin.TabularInline):
    model = CouncilMemberAlias
    extra = 1


class CouncilMemberAdmin (admin.ModelAdmin):
    inlines = [CouncilMemberAliasInline, CouncilMemberTenureInline]
    list_display = ('real_name', 'tenure_begin')
    actions = ('merge_members',)

    # =====
    # Additional fields

    def tenure_begin(self, instance):
        return instance.tenure_begin
    tenure_begin.short_description = 'Began tenure...'

    # =====
    # Actions

    def merge_members(self, request, members):
        opts = CouncilMember._meta
        if not self.has_change_permission(request, None):
            raise PermissionDenied
        return HttpResponseRedirect(
            reverse('admin:%s_%s_merge' % (opts.app_label, opts.module_name), current_app=self.admin_site.name)
            + "?" + '&'.join(['members=%s' % (member.pk,) for member in members]))
    merge_members.short_description = ugettext_lazy("Merge aliases and legislation from %(verbose_name_plural)s")

    # =====
    # Overrides

    def queryset(self, request):
        qs = super(CouncilMemberAdmin, self).queryset(request)
        qs = qs.annotate(tenure_begin=Max('tenures__begin'))
        return qs

    def get_urls(self):
        from django.conf.urls import patterns, url

        opts = CouncilMember._meta
        urlpatterns = super(CouncilMemberAdmin, self).get_urls()
        mergepatterns = patterns('',
            url(r'^merge/$',
                self.admin_site.admin_view(MergeCouncilMembersView.as_view()),
                name='%s_%s_merge' % (opts.app_label, opts.module_name)),
            )

        return mergepatterns + urlpatterns


admin.site.register(LegFile, LegFileAdmin)
admin.site.register(LegMinutes, LegMinutesAdmin)
admin.site.register(LegVote, admin.ModelAdmin)
admin.site.register(CouncilMember, CouncilMemberAdmin)
admin.site.register(MetaData_Word, WordAdmin)
admin.site.register(MetaData_Location, LocationAdmin)
admin.site.register(MetaData_Topic, admin.ModelAdmin)
admin.site.register(LegFileMetaData)
admin.site.register(CouncilDistrict, admin.OSMGeoAdmin)
admin.site.register(CouncilDistrictPlan, CouncilDistrictPlanAdmin)
