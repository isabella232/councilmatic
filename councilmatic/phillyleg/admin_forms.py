from django import forms
from django.utils.translation import ugettext as _


def merge_councilmember_form_factory(members_qs):
    class MergeCouncilMemberForm (forms.Form):
        primary = forms.ModelChoiceField(queryset=members_qs, help_text=_("This is the councilmember whose real name will be preserved. All information from other councilmembers will be merged into this one."))
        members = forms.ModelMultipleChoiceField(queryset=members_qs, initial=members_qs, widget=forms.MultipleHiddenInput())

        def merge(self):
            primary_member = self.cleaned_data['primary']
            other_members = members_qs.exclude(pk=primary_member.pk)
            
            seen_aliases = set(alias.name for alias in primary_member.aliases.all())
            for member in other_members.prefetch_related('aliases', 'tenures', 'legislation', 'votes'):

                new_aliases = member.aliases.all().exclude(name__in=seen_aliases)
                seen_aliases.update([a.name for a in member.aliases.all()])
                new_aliases.update(member=primary_member)

                member.tenures.all().update(councilmember=primary_member)
                member.votes.all().update(voter=primary_member)
                primary_member.legislation.add(*member.legislation.all())

            other_members.delete()
    return MergeCouncilMemberForm