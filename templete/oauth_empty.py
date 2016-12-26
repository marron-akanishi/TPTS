import tweepy as tp

oauth_keys = {
    'CONSUMMER_KEY' : '',
    'CONSUMMER_SECRET' : '',
    'ACCESS_TOKEN_KEY' : '',
    'ACCESS_TOKEN_SECRET' : ''
}

def get_oauth():
    """oauth_keysから各種キーを取得し、OAUTH認証を行う"""
    consumer_key, consumer_secret = \
        oauth_keys['CONSUMMER_KEY'], oauth_keys['CONSUMMER_SECRET']
    access_key, access_secret = \
        oauth_keys['ACCESS_TOKEN_KEY'], oauth_keys['ACCESS_TOKEN_SECRET']
    auth = tp.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return auth