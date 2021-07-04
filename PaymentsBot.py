import random
import time
import requests
from bs4 import BeautifulSoup as soup
import tweepy
import os
import datetime

url = ["https://thepaypers.com/news/all",
       "https://pn.glenbrook.com/",
       "https://www.finextra.com/latest-news",
       "https://www.pymnts.com/today-on-pymnts/",
       "https://www.paymentscardsandmobile.com/news/"]

# getting past the 403 Forbidden error (https://www.youtube.com/watch?v=6RfyXcf_vQo)
header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/91.0.4472.106 Safari/537.36'}

# to store news titles and links
all_news = []


def collect_news():
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
            elif site == 3:
                return content.findAll('li', {"class": "infinite-post"})[news_item].find('a', href=True, title=True)
            elif site == 4:
                return content.findAll('div', {"class": "news_infoinside single_inside div"})[news_item].find('a',
                                                                                                              href=True)

        def store_title():
            if site == 0 or site == 1 or site == 2:
                return a_find.text
            elif site == 3:
                return a_find.attrs['title']
            elif site == 4:
                return a_find.find('h2').text

        def store_link():
            if site != 2:
                return a_find.attrs['href']
            else:
                return "https://www.finextra.com/" + a_find.attrs['href']

        def number_of_loops():
            if site == 0 or site == 2:          # Payers and Finextra post news frequently
                return 20
            if site == 1 or site == 3:          # Glenbrook does 10-12 news each day, and same for Pymnts
                return 10
            if site == 4:                       # Pymnts and Payments Cards & Mobile post less frequently
                return 6

        for news_item in range(len(news)):
            copy = news[news_item]
            try:
                a_find = narrow_to_link_and_title()
            except AttributeError:
                a_find = None
                continue

            if a_find != None and store_title() != None:
                if len(list(store_title())) != 0:
                    prop_of_blanks = int(list(store_title()).count(' ')) / int(len(list(store_title())))

                    if list(store_title()).count(' ') >= 4 and prop_of_blanks < 0.3 \
                            and list(store_title())[0] != '\n':
                        if i <= number_of_loops():
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
    return all_news

# list of hashtags based on words appearing in the news title
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
                "acquire": "Acquisition",
                "crypto": "Crypto",
                "cryptocurrency": "Crypto",
                "bitcoin": "Bitcoin",
                "Bitcoin": "BTC",
                "ethereum": "Ethereum",
                "Ethereum": "Ethereum"}

# selecting the tweet from the list of tweets
def tweet_news():
    row_no = random.choice(range(len(all_news)))
    tweet_body = all_news[row_no][0]
    tweet = tweet_body

    # adding hashtags based on tweet content
    for word in hashtag_dict:
        if word in tweet.split():
            tweet = tweet + "\n" + "#" + hashtag_dict[word]
        else:
            continue

    tweet_link = all_news[row_no][1]
    tweet = tweet + "\n" + "#Payments\n" + tweet_link

    if len(list(tweet)) <= 280:
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

interval = 60 * 30

now = datetime.datetime.now()

while True:
    try:
        if now.strftime("%A") == 'Sunday' and int(now.strftime("%H")) < 24:          # to not post on sunday
            print("No news on Sunday")
            time.sleep(interval * 2)
        else:
            collect_news()
            selected_tweet = tweet_news()
            api.update_status(selected_tweet)
            time.sleep(interval)
    except tweepy.TweepError as error:
        if error.api_code == 187 or error.api_code == 170:
            print('Ignore')