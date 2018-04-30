from stream_framework.verbs import register
from stream_framework.verbs.base import Verb


class Like(Verb):
    id = 5
    infinitive = 'like'
    past_tense = 'liked'

register(Like)