from django.shortcuts import render

# Create your views here.
from django.template import RequestContext
from rest_framework import views
from rest_framework.response import Response

from apps.feed.feed_managers import manager
from apps.feed.models import Pin


class TimeLine(views.APIView):

    def get(self, request, format=None):
        feed = manager.get_feeds(request.user.id)['normal']
        # if request.REQUEST.get('delete'):
        #     feed.delete()
        activities = list(feed[:25])
        print(activities)
        # if request.REQUEST.get('raise'):
        #     raise Exception
        feed_pins = enrich_activities(activities)
        return Response(feed_pins)


def enrich_activities(activities):
    '''
    Load the models attached to these activities
    (Normally this would hit a caching layer like memcached or redis)
    '''
    like_ids = [a.object_id for a in activities]
    print(type(like_ids), 'id')
    # like_dict = Pin.objects.in_bulk(like_ids)
    # print(type(like_dict))
    like_dict = Pin.objects.filter(pk__in=like_ids).values()
    # for a in activities:
    #     a.pin = like_dict.get(a.object_id)
    #     print(a.pin.pk, 'pk')
    # return activities
    return like_dict