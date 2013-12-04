from django import forms
from councilmatic.subscriptions.models import Subscriber, Subscription

class SubscriberForm (forms.Form):
    subscriptions = forms.ModelMultipleChoiceField(queryset=Subscription.objects.all(), required=False)
