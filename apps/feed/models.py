from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_naive
import pytz

from apps.feed.feed_managers import manager


class BaseModel(models.Model):

    class Meta:
        abstract = True


class Item(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='items')
    source_url = models.TextField()
    message = models.TextField(blank=True, null=True)
    pin_count = models.IntegerField(default=0)

    # class Meta:
    #    db_table = 'pinterest_example_item'


class Board(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField()


class Pin(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item,on_delete=models.SET_NULL, null=True)
    board = models.ForeignKey(Board,on_delete=models.SET_NULL, null=True)
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='influenced_pins',
        on_delete=models.SET_NULL, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def create_activity(self):
        from stream_framework.activity import Activity
        from apps.feed.verbs import Pin as PinVerb
        activity = Activity(
            self.user_id,
            PinVerb,
            self.id,
            self.influencer_id,
            time=make_naive(self.created_at, pytz.utc),
            extra_context=dict(item_id=self.item_id)
        )
        return activity


class Follow(BaseModel):

    '''
    A simple table mapping who a user is following.
    For example, if user is Kyle and Kyle is following Alex,
    the target would be Alex.
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='following_set',
        on_delete=models.SET_NULL, null=True)
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='follower_set',
        on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

def my_post_save_handler(sender, instance, **kwargs):
    # post_save.disconnect(my_post_save_handler, sender=sender)
    # instance.do_stuff()
    # instance.save()
    manager.add_pin(instance)
    print('activity created')
    post_save.connect(my_post_save_handler, sender=sender)

post_save.connect(my_post_save_handler, sender=Pin)


from apps.feed import verbs
