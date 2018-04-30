from stream_framework.aggregators.base import RecentVerbAggregator
from stream_framework.feeds.aggregated_feed.redis import RedisAggregatedFeed
from stream_framework.feeds.redis import RedisFeed


class LikeFeed(RedisFeed):
    key_format = 'feed:normal:%(user_id)s'


class AggregatedLikeFeed(RedisAggregatedFeed):
    aggregator_class = RecentVerbAggregator
    key_format = 'feed:aggregated:%(user_id)s'


class UserLikeFeed(LikeFeed):
    key_format = 'feed:user:%(user_id)s'
