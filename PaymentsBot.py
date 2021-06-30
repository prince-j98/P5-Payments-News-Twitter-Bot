import random
import time
import requests
from bs4 import BeautifulSoup as soup
import tweepy
import os

url = ["https://thepaypers.com/news/all",
       "https://pn.glenbrook.com/",
       "https://www.finextra.com/latest-news"]


# getting past the 403 Forbidden error (https://www.youtube.com/watch?v=6RfyXcf_vQo)
header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
          'AppleWebKit/537.36 (KHTML, like Gecko) '
          'Chrome/91.0.4472.106 Safari/537.36'}

all_news = []                              # to remove repeat news and to store in one list

for site in range(len(url)):
    response_page = requests.get(url[site], headers=header)
    content = soup(response_page.content, 'html.parser')

    news = content.findAll("div")

    i = 0

    def narrow_to_link_and_title():
        if site == 0:
            return copy.find('a', href=True)
        elif site == 1:
            return copy.find('h3').find('a', href=True)
        elif site == 2:
            return copy.find('h4').find('a', href=True)

    def store_title():
        return a_find.text

    def store_link():
        if site != 2:
            return a_find.attrs['href']
        else:
            return "https://www.finextra.com/" + a_find.attrs['href']

    for news_item in range(len(news)):
        copy = news[news_item]
        try:
            a_find = narrow_to_link_and_title()
        except AttributeError:
            a_find = None
            continue

        if a_find != None and a_find.text != None:
            if len(list(a_find.text)) != 0:
                prop_of_blanks = int(list(a_find.text).count(' ')) / int(len(list(a_find.text)))

                if list(a_find.text).count(' ') >= 4 and prop_of_blanks < 0.3 \
                        and list(a_find.text)[0] != '\n':
                    if i <= 15:
                        i += 1
                        dict_news = [store_title(), store_link()]
                        all_news.append(dict_news)

                        try:
                            if all_news[-1] == all_news[-2]:
                                all_news.pop()
                                i -= 1
                            else:
                                continue
                        except IndexError:
                            continue
                    else:
                        break
            else:
                continue
        else:
            continue
print("\n")

hashtag_dict = {"mobile": "Mobile",
                "bank": "Banking",
                "Bank": "Banking",
                "Fintech": "Fintech",
                "fintech": "Fintech",
                "India": "India",
                "Financial": "Financial",
                "financial": "Financial",
                "financing": "Funding",
                "BNPL": "BNPL",
                "Buy Now, Pay Later": "BNPL",
                "Buy Now Pay Later": "BNPL",
                "bnpl": "BNPL",
                "QR": "QR",
                "Open Banking": "Open Banking",
                "Visa": "Visa",
                "Stripe": "Stripe",
                "Mastercard": "Mastercard",
                "Funding": "Funding",
                "raises": "Funding",
                "Accounts": "Banking",
                "travel": "Travel",
                "acquires": "Acquisition",
                "acquire": "Acquisition"}

def tweet_news():
    row_no = random.choice(range(len(all_news)))
    tweet_body = all_news[row_no][0]
    tweet = tweet_body

    # adding hashtags based on tweet content
    for i in hashtag_dict:
        if i in tweet.split():
            tweet = tweet + "\n" + "#" + hashtag_dict[i]
        else:
            continue

    tweet_link = all_news[row_no][1]
    tweet = tweet + "\n" + "#Payments\n" + tweet_link

    if len(list(tweet)) <=280:
        return tweet
    else:
        tweet_news()

# Tweeting the news

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

interval = 60 * 45

while True:
    api.update_status(tweet_news())
    time.sleep(interval)