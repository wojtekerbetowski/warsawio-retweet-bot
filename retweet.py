# -*- coding: utf-8 -*-
import tweepy
import os
import logging
import logentries
import redis


# Check environment vars
CONSUMER_KEY        = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET     = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN        = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
REDIS_HOST          = os.environ["REDIS_HOST"]
REDIS_PORT          = os.environ["REDIS_PORT"]
REDIS_PASSWORD      = os.environ["REDIS_PASSWORD"]
LOGENTRIES_TOKEN    = os.environ["LOGENTRIES_TOKEN"]

# Configure logger
log = logging.getLogger('logentries')
log.setLevel(logging.DEBUG)
logentries_handler = logentries.LogentriesHandler(LOGENTRIES_TOKEN)
log.addHandler(logentries_handler)


try:
    # Connect to Redis database
    redis_connection = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
    )
    assert redis_connection.ping()

    # connect to Twitter
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # your hashtag or search query and tweet language (empty = all languages)
    hashtag = "#warsawio"
    tweetLanguage = ""

    # blacklisted users and words
    userBlacklist = ["warsawIO", "bobthenoob2"]
    wordBlacklist = ["RT", u"♺"]

    # retrieve last savepoint if available
    savepoint = redis_connection.get('last_id_hashtag_warsawio')
    log.debug("Using last checkpoint: {}".format(savepoint))

    # search query
    timelineIterator = tweepy.Cursor(
        api.search,
        q=hashtag,
        since_id=savepoint,
        lang=tweetLanguage
    ).items()

    # put everything into a list to be able to sort/filter
    timeline = [x for x in timelineIterator]

    try:
        last_tweet_id = timeline[0].id
    except IndexError as e:
        last_tweet_id = savepoint

    # filter @replies/blacklisted words & users out and reverse timeline
    #timeline = filter(lambda status: status.text[0] != "@", timeline)
    timeline = filter(lambda status: not any(word in status.text.split() for word in wordBlacklist), timeline)
    timeline = filter(lambda status: status.author.screen_name not in userBlacklist, timeline)
    timeline.reverse()

    tw_counter = 0
    err_counter = 0

    # iterate the timeline and retweet
    for status in timeline:
        try:
            log.debug("Retweeting: ({}) {}: {}".format(
                status.created_at,
                status.author.screen_name.encode('utf-8'),
                status.text.encode('utf-8'),
            ))

            api.retweet(status.id)
            tw_counter += 1

        except tweepy.error.TweepError as e:
            # just in case tweet got deleted in the meantime or already retweeted
            log.error("Error {}".format(e))
            err_counter += 1
            continue

    log.info("Finished. %d Tweets retweeted, %d errors occured." % (tw_counter, err_counter))

    redis_connection.set('last_id_hashtag_warsawio', last_tweet_id)

except Exception as e:
    log.error("Error occuerd: %s", e)
