from django.contrib import messages
from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from django.views.generic import FormView
from phillyleg.admin_forms import merge_councilmember_form_factory
from phillyleg.models import CouncilMember


class MergeCouncilMembersView (FormView):
    template_name = 'admin/merge_councilmembers_form.html'

    def get_form_class(self):
        self.members = self.get_members_queryset(self.request)
        return merge_councilmember_form_factory(self.members)

    def form_valid(self, form):
        form.merge()
        messages.success(self.request, 'Successfully merged %s council members into %s' % (self.members.count(), form.cleaned_data['primary']))
        return super(MergeCouncilMembersView, self).form_valid(form)

    def get_success_url(self):
        opts = CouncilMember._meta
        memberlisturl = reverse('admin:%s_%s_changelist' %
                                (opts.app_label, opts.module_name),
                                current_app=admin.site.name)
        return memberlisturl

    def get_context_data(self, **kwargs):
        opts = CouncilMember._meta
        kwargs.update({
            "objects": self.members,
            "opts": opts,
            "app_label": opts.app_label,
        })
        return super(MergeCouncilMembersView, self).get_context_data(**kwargs)

    def get_members_queryset(self, request):
        member_pks = [int(pk_str) for pk_str in request.REQUEST.getlist('members')]
        members_qs = CouncilMember.objects.filter(pk__in=member_pks)
        return members_qs


