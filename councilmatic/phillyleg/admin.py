from django.contrib.gis import admin
from django.db.models import Max
from django.utils.translation import ugettext_lazy
from phillyleg.models import *



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

    def queryset(self, request):
        qs = super(CouncilMemberAdmin, self).queryset(request)
        qs = qs.annotate(tenure_begin=Max('tenures__begin'))
        return qs

    def tenure_begin(self, instance):
        return instance.tenure_begin
    tenure_begin.short_description = 'Began tenure...'

    def get_merge_form(self, members):
        class MergeCouncilMemberForm (django.forms.Form):
            primary = django.forms.ModelChoiceField(queryset=members)
            members = django.forms.ModelMultipleChoiceField(queryset=members)

            def merge(self):
                seen_aliases = [alias.name for alias in primary.aliases.all()]
                for member in self.members.all():
                    for alias in member.aliases.all():
                        if alias.name not in seen_aliases:
                            seen_aliases.add(alias.name)
                            alias.member = self.primary
                            alias.save()

                    for tenure in member.tenures.all():
                        tenure.member = self.primary
                        tenure.save()

                    for legislation in member.legislation.all():
                        legislation.sponsors.remove(member)
                        legislation.sponsors.add(self.primary)

                    for vote in member.votes.all():
                        vote.voter = self.primary
                        vote.save()

                    member.delete()

    def merge_members(self, request, members):
        opts = CouncilMember._meta
        app_label = opts.app_label

        if request.POST.get('post'):
            # Do the merge
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_text(opts.verbose_name)
        else:
            objects_name = force_text(opts.verbose_name_plural)

        context = {
            "title": title,
            "queryset": queryset,
            "opts": opts,
            "app_label": app_label,
            "form": self.get_merge_form()
        }

        # Display the confirmation page
        render(request, 'admin/merge_councilmembers_form.html', context)
    merge_members.short_description = ugettext_lazy("Delete selected %(verbose_name_plural)s")


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
