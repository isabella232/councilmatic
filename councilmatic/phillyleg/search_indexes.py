import datetime
from itertools import chain
from haystack import indexes
from phillyleg.models import LegFile, LegMinutes, LegFileMetaData


class LegislationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    is_blank = indexes.BooleanField()
    file_id = indexes.CharField(model_attr='id')
    topics = indexes.MultiValueField()
    status = indexes.CharField(model_attr='status')
    controlling_body = indexes.CharField(model_attr='controlling_body')
    file_type = indexes.CharField(model_attr='type')
    key = indexes.IntegerField(model_attr='key')
    sponsors = indexes.MultiValueField()

    order_date = indexes.DateField(model_attr='intro_date')

    def get_model(self):
        return LegFile

    def prepare_is_blank(self, leg):
        return leg.title.strip() == ''
    
    def prepare_sponsors(self, leg):
        return (
            [sponsor.real_name for sponsor in leg.sponsors.all()] +
            [alias.name for alias in chain(*(sponsor.aliases.all() for sponsor in leg.sponsors.all()))]
        )

    def prepare_topics(self, leg):
        try:
            return [topic.topic for topic in leg.metadata.topics.all()]
        except LegFileMetaData.DoesNotExist:
            # The only time this should happen is when the legfile is first
            # saved. A signal gets sent that updates the index for the object
            # before the legfile's metadata has a chance to be created. We're
            # just going to have to accept it in this case.
            pass

    def get_updated_field(self):
        return 'updated_datetime'


class MinutesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='fulltext')
    date_taken = indexes.DateField(null=True)

    order_date = indexes.DateField(model_attr='date_taken')

    def get_model(self):
        return LegMinutes

    def get_updated_field(self):
        return 'updated_datetime'
