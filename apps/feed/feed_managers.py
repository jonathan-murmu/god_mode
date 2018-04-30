from stream_framework.feed_managers.base import Manager, FanoutPriority
from apps.feed.like_feed import LikeFeed, AggregatedLikeFeed, UserLikeFeed
from apps.feed.models import Follow


class LikeManager(Manager):
    # this example has both a normal feed and an aggregated feed (more like
    # how facebook or wanelo uses feeds)
    feed_classes = dict(
        normal=LikeFeed,
        aggregated=AggregatedLikeFeed
    )
    user_feed_class = UserLikeFeed

    def add_like(self, like):
        activity = like.create_activity()
        # add user activity adds it to the user feed, and starts the fanout
        self.add_user_activity(like.user_id, activity)

    def remove_like(self, like):
        activity = like.create_activity()
        # removes the pin from the user's followers feeds
        self.remove_user_activity(like.user_id, activity)

    def get_user_follower_ids(self, user_id):
        ids = Follow.objects.filter(target=user_id).values_list('user_id', flat=True)
        return {FanoutPriority.HIGH:ids}

manager = LikeManager()