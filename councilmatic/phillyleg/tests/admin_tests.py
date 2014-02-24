import datetime as dt
from django.test import TestCase, RequestFactory
from phillyleg.models import CouncilMember, CouncilMemberAlias, CouncilMemberTenure, LegFile, LegVote
from phillyleg.admin import MergeCouncilMembersView
from phillyleg.admin_forms import merge_councilmember_form_factory
from nose.tools import assert_equal, assert_in, assert_true, nottest
from django_nose.tools import assert_num_queries

class MergeCouncilmembersTest (TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.cm1 = CouncilMember.objects.create(real_name='Mjumbe Poe')
        self.cm2 = CouncilMember.objects.create(real_name='Mjumbe Wawatu Poe')

        self.aliases = [
            CouncilMemberAlias.objects.create(member=self.cm1, name='Mjumbe Poe'),
            CouncilMemberAlias.objects.create(member=self.cm1, name='Councilmember Poe'),
            CouncilMemberAlias.objects.create(member=self.cm1, name='Councilmember M. Poe'),
            CouncilMemberAlias.objects.create(member=self.cm2, name='Mjumbe Poe'),
            CouncilMemberAlias.objects.create(member=self.cm2, name='Mjumbe W. Poe'),
            CouncilMemberAlias.objects.create(member=self.cm2, name='mjumbewu')
        ]

        self.tenures = [
            CouncilMemberTenure.objects.create(councilmember=self.cm1, begin=dt.date(2008,12,14), end=dt.date(2010,12,13)),
            CouncilMemberTenure.objects.create(councilmember=self.cm1, begin=dt.date(2010,12,14), end=dt.date(2012,12,13)),
            CouncilMemberTenure.objects.create(councilmember=self.cm2, begin=dt.date(2006,12,14), end=dt.date(2008,12,13)),
            CouncilMemberTenure.objects.create(councilmember=self.cm2, begin=dt.date(2012,12,14))
        ]

        self.legfiles = [
            LegFile.objects.create(key=1209, id='abc'),
            LegFile.objects.create(key=3487, id='def'),
            LegFile.objects.create(key=5665, id='ghi'),
            LegFile.objects.create(key=7843, id='jkl'),
        ]
        self.cm1.legislation.add(self.legfiles[0], self.legfiles[1])
        self.cm2.legislation.add(self.legfiles[2], self.legfiles[3])

    def tearDown(self):
        for a in self.aliases: a.delete()
        for t in self.tenures: t.delete()
        for l in self.legfiles: l.delete()
        self.cm1.delete()
        self.cm2.delete()

    def test_has_appropriate_members_queryset(self):
        request = self.factory.get('?members=%s&members=%s' % (self.cm1.pk, self.cm2.pk))
        members_qs = MergeCouncilMembersView().get_members_queryset(request)
        assert_equal(len(members_qs), 2)
        assert_in(self.cm1, members_qs)
        assert_in(self.cm2, members_qs)

    def test_GET_has_merge_form_with_members(self):
        request = self.factory.get('?members=%s&members=%s' % (self.cm1.pk, self.cm2.pk))
        view = MergeCouncilMembersView.as_view()
        response = view(request)
        assert_in('form', response.context_data)
        assert_in(self.cm1, response.context_data['form'].fields['primary'].queryset)
        assert_in(self.cm2, response.context_data['form'].fields['primary'].queryset)

    def test_POST_with_invalid_form_rerenders_successfully(self):
        request = self.factory.post('', data={'members': [self.cm1.pk, self.cm2.pk]})
        view = MergeCouncilMembersView.as_view()
        response = view(request)
        assert_equal(response.status_code, 200)

    @nottest
    def base_reassignment_test(self):
        form_class = merge_councilmember_form_factory(
            CouncilMember.objects.filter(pk__in=[self.cm1.pk, self.cm2.pk]))
        form = form_class({'primary': self.cm2.pk, 'members': [self.cm1.pk, self.cm2.pk]})
        assert_true(form.is_valid(), form.errors)
        return form

    def test_form_merge_reassigns_aliases(self):
        form = self.base_reassignment_test()
        form.merge()
        aliases = self.cm2.aliases.all()
        assert_equal(aliases.count(), 5)
        assert_equal(set([alias.name for alias in aliases]), set([alias.name for alias in self.aliases]))

    def test_form_merge_reassigns_tenures(self):
        form = self.base_reassignment_test()
        form.merge()
        tenures = self.cm2.tenures.all()
        assert_equal(tenures.count(), 4)
        assert_equal(set([tenure.begin for tenure in tenures]), set([tenure.begin for tenure in self.tenures]))

    def test_form_merge_reassigns_legislation(self):
        form = self.base_reassignment_test()
        form.merge()
        legfiles = self.cm2.legislation.all()
        assert_equal(legfiles.count(), 4)
        assert_equal(set([legfile.key for legfile in legfiles]), set([legfile.key for legfile in self.legfiles]))

    def test_form_merge_runs_finite_queries(self):
        form = self.base_reassignment_test()

        # Prefetches
        # ----------
        # Constant number, no matter how many councilmembers
        #
        #     SELECT * FROM alias
        #      WHERE member_id = <primary_member_id>;
        #     
        #     SELECT * FROM councilmember
        #      WHERE id IN (<member_ids>)
        #        AND NOT (id = <primary_member_id>);
        #     
        #     SELECT * FROM alias
        #      WHERE member_id IN (<nonprimary_member_ids>);
        #     
        #     SELECT * FROM tenure
        #      WHERE councilmember_id IN (<nonprimary_member_ids>);
        #     
        #     SELECT * FROM legfile
        #        INNER JOIN legfile_sponsors ON (key = legfile_sponsors.legfile_id)
        #      WHERE councilmember_id IN (<nonprimary_member_ids>);
        #     
        #     SELECT * FROM legvote
        #      WHERE voter_id IN (<nonprimary_member_ids>);
        #     
        prefetch_q_count = 6

        # Reassignments
        # -------------
        # Linear with the number of members
        #
        #     UPDATE alias
        #        SET member_id = <primary_member_id>
        #      WHERE member_id = <nonprimary_member_id>
        #        AND NOT ("name" IN (<already_known_aliases>));
        #     
        #     UPDATE tenure
        #        SET councilmember_id = <primary_member_id>
        #      WHERE councilmember_id = <nonprimary_member_id>;
        #     
        #     UPDATE legvote
        #        SET voter_id = <primary_member_id>
        #      WHERE voter_id = <nonprimary_member_id>;
        #     
        #     SELECT legfile_id FROM legfile_sponsors
        #      WHERE councilmember_id = <primary_member_id>
        #        AND legfile_id IN (<nonprimary_member's legislation_ids>));
        #     
        #     INSERT INTO legfile_sponsors (legfile_id, councilmember_id)
        #          VALUES <nonprimary_member's legislation>;
        reassignment_q_count = 5

        # Deletions
        # ---------
        # Constant number, no matter how many members
        #
        #     SELECT * FROM councilmember
        #      WHERE id IN (<member_ids>)
        #        AND NOT (id = <primary_member_id>);
        #     
        #     SELECT * FROM alias
        #      WHERE member_id IN (<nonprimary_member_ids>);
        #     
        #     SELECT * FROM tenure
        #      WHERE councilmember_id IN (<nonprimary_member_ids>);
        #     
        #     SELECT * FROM legfile_sponsors
        #      WHERE councilmember_id IN (<nonprimary_member_ids>);
        #     
        #     SELECT * FROM legvote
        #      WHERE voter_id IN (<nonprimary_member_ids>);
        #     
        #     DELETE FROM legfile_sponsors
        #      WHERE id IN (<nonprimary_members' sponsorships>);
        #     
        #     DELETE FROM alias
        #      WHERE id IN (<nonprimary_members' duplicate aliases>);
        #     
        #     DELETE FROM councilmember
        #      WHERE id IN (<nonprimary_member_ids>);
        deletion_q_count = 8

        with assert_num_queries(prefetch_q_count + reassignment_q_count + deletion_q_count):
            form.merge()
