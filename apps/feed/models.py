from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals, F
from django.utils.text import slugify
from django.utils.timezone import make_naive, is_aware
import pytz
from stream_django import feed_manager
from stream_django.activity import create_reference
from stream_framework import activity


class Posts(models.Model):
    """Blog posts."""
    post = models.TextField(max_length=1000)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Like(models.Model):
    """Model to store the Likes."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Posts, on_delete=models.SET, null=True)
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='influenced_likes',
        on_delete=models.SET_NULL, null=True
    )
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def create_activity(self):
        from stream_framework.activity import Activity
        from .verbs import Like as LikeVerb
        activity = Activity(
            self.user_id,
            LikeVerb,
            self.id,
            self.influencer_id,
            time=make_naive(self.created_at, pytz.utc),
            extra_context=dict(item_id=self.post_id)
        )
        print(activity)
        return activity


class Follow(models.Model):
    """A simple table mapping who a user is following.

    For example, if user is Kyle and Kyle is following Alex,
    the target would be Alex.
    user following target; target's follower is user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='following_set',
        on_delete=models.SET_NULL, null=True
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='follower_set',
        on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class Tweet(activity.Activity, models.Model):
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE)
    text = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def print_self(self):
        print(self.text)

    @property
    def activity_object_attr(self):
        return self

    @property
    def activity_verb(self):
        model_name = slugify(self.__class__.__name__)
        return model_name

    @property
    def activity_object(self):
        return create_reference(self.activity_object_attr)
    @property
    def activity_foreign_id(self):
        return self.activity_object
    @property
    def activity_time(self):
        atime = self.created_at
        if is_aware(self.created_at):
            atime = make_naive(atime, pytz.utc)
        return atime

    def save(self):
        self.create_hashtags()
        super(Tweet, self).save()

    def create_hashtags(self):
        hashtag_set = set(self.parse_hashtags())
        for hashtag in hashtag_set:
            h, created = Hashtag.objects.get_or_create(name=hashtag)
            h.save()
        Hashtag.objects.filter(name__in=hashtag_set).update(occurrences=F('occurrences')+1)

    def parse_hashtags(self):
        return [slugify(i) for i in self.text.split() if i.startswith("#")]

    def parse_mentions(self):
        mentions = [slugify(i) for i in self.text.split() if i.startswith("@")]
        return User.objects.filter(username__in=mentions)

    def parse_all(self):
        parts = self.text.split()
        hashtag_counter = 0
        mention_counter = 0
        result = {"parsed_text": "", "hashtags": [], "mentions": []}
        for index, value in enumerate(parts):
            if value.startswith("#"):
                parts[index] = "{hashtag" + str(hashtag_counter) + "}"
                hashtag_counter += 1
                result[u'hashtags'].append(slugify(value))
            if value.startswith("@"):
                parts[index] = "{mention" + str(mention_counter) + "}"
                mention_counter += 1
                result[u'mentions'].append(slugify(value))
        result[u'parsed_text'] = " ".join(parts)
        return result

    @property
    def activity_notify(self):
        targets = [feed_manager.get_news_feeds(self.user_id)['timeline']]
        for hashtag in self.parse_hashtags():
            targets.append(feed_manager.get_feed('user', 'hash_%s' % hashtag))
        for user in self.parse_mentions():
            targets.append(feed_manager.get_news_feeds(user.id)['timeline'])
        return targets


class Hashtag(models.Model):
    name = models.CharField(max_length=160)
    occurrences = models.IntegerField(default=0)


def unfollow_feed(sender, instance, **kwargs):
    feed_manager.unfollow_user(instance.user_id, instance.target_id)


def follow_feed(sender, instance, created, **kwargs):
    if created:
        feed_manager.follow_user(instance.user_id, instance.target_id)


signals.post_delete.connect(unfollow_feed, sender=Follow)
signals.post_save.connect(follow_feed, sender=Follow)