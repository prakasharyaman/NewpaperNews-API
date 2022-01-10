import time
import base64, requests, json, os, ast
from dotenv import load_dotenv
from random import randrange
from newsapi import NewsApiClient
from datetime import datetime, timedelta
COUNTRIES_LANGUAGES = {"in": "en", "us": "en", }
CATEGORIES = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
SOURCES = ["bbc-news",]

load_dotenv()

GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
API_KEYS = ast.literal_eval(os.getenv("API_KEYS"))

LAST_KEY_INDEX = randrange(0, len(API_KEYS))

print('hello world')
def get_key():
    global LAST_KEY_INDEX
    LAST_KEY_INDEX = (LAST_KEY_INDEX + 1) % len(API_KEYS)
    return API_KEYS[LAST_KEY_INDEX]

def push_to_github(filename, content):
    url = "https://api.github.com/repos/prakasharyaman/NewpaperNews-API/contents/" + filename
    base64content = base64.b64encode(bytes(json.dumps(content), 'utf-8'))
    data = requests.get(url + '?ref=main', headers={"Authorization": "token " + GITHUB_API_TOKEN}).json()
    print("trying to get data reply ")
    
    sha = data['sha']
    print(sha)
    if base64content.decode('utf-8') != data['content'].replace("\n", ""):
        message = json.dumps({"message": "update " + filename,
                              "branch": "main",
                              "content": base64content.decode("utf-8"),
                              "sha": sha
                              })

        resp = requests.put(url, data=message,
                            headers={"Content-Type": "application/json", "Authorization": "token " + GITHUB_API_TOKEN})

        print(resp)
    else:
        print("Everything up to date")


# @app.route('/')
# def hello_world():
#     return redirect("https://saurav.tech/NewsAPI/")
def update_top_headline():
    print('updating headlines')
    for category in CATEGORIES:
        for country in COUNTRIES_LANGUAGES:
            print("Started category:{0} country:{1} at :{2}".format(category, country,
                                                                    time.strftime("%A, %d. %B %Y %I:%M:%S %p")))
            newsapi = NewsApiClient(api_key=get_key())
            top_headlines = newsapi.get_top_headlines(category=category, country=country, language=COUNTRIES_LANGUAGES[country], page_size=100)
            
            push_to_github("top-headlines/category/{0}/{1}.json".format(category, country), top_headlines)


def update_everything():
    newsapi = NewsApiClient(api_key=get_key())
    for source in SOURCES:
        print("Started source:{0} : {1}".format(source, time.strftime("%A, %d. %B %Y %I:%M:%S %p")))
        all_articles = newsapi.get_everything(sources=source,
                                              from_param=(datetime.now() - timedelta(days=1, hours=5,
                                                                                     minutes=30)).date().isoformat(),
                                              language='en',
                                              sort_by='publishedAt',
                                              page_size=100)
        push_to_github("everything/{0}.json".format(source), all_articles)

update_top_headline()
