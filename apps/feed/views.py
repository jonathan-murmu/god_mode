from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from stream_django import feed_manager
from stream_django.enrich import Enrich
from apps.feed.feed_managers import manager
from apps.feed.models import Posts, Like, Hashtag

enricher = Enrich()


class TimeLine(views.APIView):

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        posts = Posts.objects.all().values()

        # print(manager.get_feeds(request.user.id))
        feed = manager.get_feeds(request.user.id)['normal']
        print(feed)
        # if request.REQUEST.get('delete'):
        #     feed.delete()
        activities = list(feed[:25])
        print(activities)
        # if request.REQUEST.get('raise'):
        #     raise (Exception, activities)
        posts = enrich_activities(activities)

        # feeds = feed_manager.get_news_feeds(self.request.user.id)
        # print(feeds)
        # activities = feeds.get('timeline').get()['results']
        # print(activities)
        # enriched_activities = enricher.enrich_activities(activities)
        #
        # activities = enriched_activities
        # context['login_user'] = self.request.user
        # context['hashtags'] = Hashtag.objects.order_by('-occurrences')

        return Response(posts)


def enrich_activities(activities):
    '''
    Load the models attached to these activities
    (Normally this would hit a caching layer like memcached or redis)
    '''
    like_ids = [a.object_id for a in activities]
    like_dict = Like.objects.in_bulk(like_ids)
    for a in activities:
        a.pin = like_dict.get(a.object_id)
    return activities