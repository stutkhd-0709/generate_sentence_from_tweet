from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session
import json
import itertools
import random
import MeCab
import re
import os

class Marcov_tw():
    def __init__(self,twitter, name):
        self.twitter = twitter
        self.name = name

    def m_tokenize(self, text):
        text=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)#URL
        text = text.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
        m = MeCab.Tagger()
        node = m.parseToNode(text)
        tokens = ["BOS"]
        while node:
            if node.surface != "":
                tokens.append(node.surface)
            node = node.next
        tokens.append("EOS")
        return tokens

    def get_tweet(self):
        #TwitterAPIの認証情報
        url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        params = {"screen_name":self.name, "count":100,"include_rts":False}
        req = self.twitter.get(url, params=params)

        if req.status_code == 200:
            timeline = json.loads(req.text)
            tweets = [tweet["text"] for tweet in timeline]
            tweets = []
            for tweet in timeline:
                text = tweet["text"].replace("\n"," ")
                tweets.append(text)
            return tweets
        else:
            return print("ERROR: %d" % req.status_code)

    #マルコフ連鎖
    def marcov_sentence(self):
        wakati_twe = [self.m_tokenize(sentence) for sentence in self.get_tweet()]
        wakati_twe = list(itertools.chain.from_iterable(wakati_twe))

        marcov = {}
        w1 = ""
        w2 = ""
        for word in wakati_twe:
            if w1 and w2:
                if (w1,w2) not in marcov:
                    marcov[(w1,w2)] = []
                marcov[(w1,w2)].append(word)
            w1, w2 = w2,word

        #一番最後はノードが無くてkeyエラーがおこる
        marcov[(w1,w2)] = ["BOS"]
        ans = ""
        eos_count = 0
        limit = 3
        # w1がBOSからはじめさせる
        while True:
            (w1,w2) = random.choice(list(marcov.keys()))
            if w1 == "BOS":
                break

        ans += (w1+w2)
        while eos_count < limit:
            next_word = random.choice(marcov[(w1,w2)])
            ans += next_word
            if w2 == "EOS":
                eos_count += 1
            (w1,w2) = (w2, next_word)
        ans = ans.replace("BOS","").replace("EOS","\n")

        #twitterの文字制限
        if len(ans) > 140:
            ans = ans[:137]
            ans += '笑笑!!'
        return ans

if  __name__ == "__main__":
    dotenv_path = '/work/.env'
    load_dotenv(dotenv_path)
    CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
    CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
    TW_418_ID = os.environ.get('TW_418_ID')

    twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    url_update = "https://api.twitter.com/1.1/statuses/update.json"
    mt = Marcov_tw(twitter, TW_418_ID)
    tweet = mt.marcov_sentence()

    params = {"status" : tweet}

    req = twitter.post(url_update, params = params)

    if req.status_code == 200:
        print("Succeed!")
    else:
        print("ERROR : %d"% req.status_code)