import datetime
import phillyleg
from django.db import transaction
from django.db.utils import IntegrityError

from phillyleg.models import *

identity = lambda x: x

def unique(iterable, key=None):
    key = key or identity
    seen = set()
    for elem in iterable:
        elem_key = key(elem)
        if elem_key not in seen:
            seen.add(elem_key)
            yield elem


class CouncilmaticDataStoreWrapper (object):
    """
    This is the interface over an arbitrary database where the information is
    being stored.  I'm using it primarily because I want the scraper code to be
    used on both ScraperWiki and in my Django app on my Django models.  For my
    app, I want local access to the data.  But I love ScraperWiki as a central
    place where you can find data about anything you want, so it's important to
    have the data available on SW as well.
    """
    STARTING_KEY = 72

    def get_latest_key(self):
        '''Check the datastore for the key of the most recent filing.'''

        records = LegFile.objects.order_by('-key')
        try:
            return records[0].key
        except IndexError:
            return self.STARTING_KEY

    def get_continuation_key(self):
        records = LegKeys.objects.all()
        try:
            return records[0].continuation_key
        except IndexError:
            return self.STARTING_KEY

    def save_continuation_key(self, key):
        try:
            keys = LegKeys.objects.get(pk=1)
        except LegKeys.DoesNotExist:
            keys = LegKeys(pk=1)

        keys.continuation_key = key
        keys.save()

    def has_text_changed(self, key, new_legfile):
        """
        Check if the legfile text has changed to determine whether the metadata
        should be updated on save.  If not, then for the sake of time we may
        just not update it.
        """
        try:
            old_legfile = LegFile.objects.get(key=key)

            # For now, the text is just the contents of the title
            return old_legfile.title != new_legfile.title

        except LegFile.DoesNotExist:
            return True

    @transaction.commit_on_success
    def save_legis_file(self, file_record, attachment_records,
                        action_records, minutes_records):
        """
        Take a legislative file record and do whatever needs to be
        done to get it into the database.
        """
        file_record = self.__convert_or_delete_date(file_record, 'intro_date')
        file_record = self.__convert_or_delete_date(file_record, 'final_date')

        # Don't include the sponsors list, as the model framework doesn't allow
        # batch inserting of lists for a ManyToManyField, and we will need to
        # insert each sponsor individually.  See below in 'Create the record'.
        sponsor_names = file_record['sponsors']
        del file_record['sponsors']

        # Topics become tags
        topic_names = file_record.pop('topics', [])

        # Create the record
        try:
            legfile = LegFile.objects.get(key=file_record['key'])
        except LegFile.DoesNotExist:
            legfile = LegFile(key=file_record['key'])

        legfile.update(file_record, commit=False)

        # Changing the text in a legfile is an expensive operation.  Not only
        # do we save the file, but also a record for each unique word in the
        # file.  So, if we can avoid updating that metadata we should.
        changed = self.has_text_changed(legfile.key, legfile)
        legfile.save(update_words=changed, update_mentions=changed, update_locations=changed)

        existing_sponsors = legfile.sponsors.all().prefetch_related('aliases')
        existing_topics = legfile.metadata.topics.all()

        if isinstance(sponsor_names, basestring):
            sponsor_names = [name.strip() for name in sponsor_names.split(',')]

        # Only consider unique councilmember names. This protects against 
        # errors in the source data such as at http://phila.legistar.com/LegislationDetail.aspx?ID=1448369&GUID=854AA05E-BE3F-4ED4-A7D4-D7CFF00987FE
        for sponsor_name in unique(sponsor_names):
            if sponsor_name is None or len(sponsor_name) == 0:
                continue

            try:
                sponsor = CouncilMember.objects.get(aliases__name=sponsor_name)
            except CouncilMember.DoesNotExist:
                sponsor = CouncilMember.objects.create(real_name=sponsor_name)
                alias = CouncilMemberAlias.objects.create(member=sponsor, name=sponsor_name)

            # Add the legislation to the sponsor and save, instead of the other
            # way around, because saving legislation can be expensive.
            if sponsor not in existing_sponsors :
                sponsor.legislation.add(legfile)
                sponsor.save()

        for topic_name in topic_names:
            topic, created = MetaData_Topic.objects.get_or_create(topic=topic_name)
            if topic not in existing_topics:
                legfile.metadata.topics.add(topic)

        # Create notes attached to the record
        for attachment_record in attachment_records:
            attachment_record = self.__replace_key_with_legfile(attachment_record)
            self._save_or_ignore(LegFileAttachment, attachment_record)

        # Create minutes
        for minutes_record in minutes_records:
            self._save_or_ignore(LegMinutes, minutes_record)

        # Create actions attached to the record
        for action_record in action_records:
            action_record = self.__replace_key_with_legfile(action_record)
            action_record = self.__replace_url_with_minutes(action_record)
            votes = action_record.pop('votes', [])
            action = None
            if not self.is_duplicate_action(action_record):
                action = self._save_or_ignore(LegAction, action_record)

            if action is None:
                continue

            for vote_record in votes:
                vote_record['action'] = action
                voter_name = vote_record['voter']
                voter, created = CouncilMember.objects.get_or_create(name=voter_name)
                vote_record['voter'] = voter
                vote = self._save_or_ignore(LegVote, vote_record)
                
    def is_duplicate_action(self, action_record):
        """
        Check whether the given action_record data already exists in the
        database.
        """
        date_taken = action_record.get('date_taken')
        legfile = action_record.get('file')
        actions = LegAction.objects.filter(date_taken=date_taken, file=legfile)

        for action in actions:
            if action.description == action_record.get('description') and \
               action.notes == action_record.get('notes'):
                return True

        return False

    @property
    def pdf_mapping(self):
        """
        Build a mapping of the URLs and PDF test that already exist in the
        database.
        """
        mapping = {}

        for attachment in LegFileAttachment.objects.all():
            mapping[attachment.url] = attachment.fulltext

        for minutes in LegMinutes.objects.all():
            mapping[minutes.url] = minutes.fulltext

        return mapping

    def __convert_or_delete_date(self, file_record, date_key):
        if file_record[date_key]:
            pass
#            file_record[date_key] = datetime.datetime.strptime(
#                file_record[date_key], '%m/%d/%Y')
        else:
            del file_record[date_key]

        return file_record

    __legfile_cache = {}
    def __replace_key_with_legfile(self, record):
        key = record['key']

        if key not in self.__legfile_cache:
            legfile = LegFile.objects.get(key=key)
            self.__legfile_cache[key] = legfile
        else:
            legfile = self.__legfile_cache[key]

        del record['key']
        record['file'] = self.__legfile_cache[key]

        return record

    __legminutes_cache = {}
    def __replace_url_with_minutes(self, record):
        # minutes is empty for hosted legistar
        minutes_url = record.pop('minutes_url', '')

        if minutes_url not in self.__legminutes_cache:
            if minutes_url == '':
                minutes = None
            else:
                try:
                    minutes = LegMinutes.objects.get(url=record['minutes_url'])
                except phillyleg.models.LegMinutes.DoesNotExist:
                    minutes = None
            self.__legminutes_cache[minutes_url] = minutes
        else:
            minutes = self.__legminutes_cache[minutes_url]

        record['minutes'] = minutes

        return record

    def _save_or_ignore(self, ModelClass, record):
        model_instance = ModelClass(**record)
        try:
            # Wrap the save in a transaction savepoint, so that if we want to
            # roll back to this point we can.  We will want to roll back if
            # there is an integrity error, as specified below.
            sid = transaction.savepoint()
            model_instance.save()
            transaction.savepoint_commit(sid)
            return model_instance
        except IntegrityError:
            # If it's a duplicate, don't worry about it.  Just move on.
            transaction.savepoint_rollback(sid)
            return None
