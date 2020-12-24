from django.shortcuts import render
from django.http import HttpResponse
from urllib.request import urlopen
import json
from collections import defaultdict
from urllib.parse import quote
from collections import Counter
from dateutil import parser
import operator
from django.utils.datastructures import MultiValueDictKeyError
from django.core.paginator import Paginator
import tweepy
from textblob import TextBlob 
import re
# Create your views here.

'''
def home(request):
    return HttpResponse('<h1>SOUL</h1>')
'''


def home(request):
    return render(request, 'dashboard/dashboard.html', {'name': 'Goutham','search_term':"search",'language':["English","Hindi","Portugese"],'Country':["India","USA","Brazil"],"ver_statuses":["Yes","No"]})


# Methods for Sentimental Analysis
def clean_tweet(tweet): 
    ''' 
    Utility function to clean tweet text by removing links, special characters 
    using simple regex statements. 
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 
  
def get_tweet_sentiment(tweet): 
    ''' 
    Utility function to classify sentiment of passed tweet 
    using textblob's sentiment method 
    '''
    # create TextBlob object of passed tweet text 
    analysis = TextBlob(clean_tweet(tweet)) 
    # set sentiment 
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'


search = ""
lang = ""
cout = ""
ver = ""

def getData(request):

    try:
        searchText = request.GET['q']
        language = request.GET['language']
        country = request.GET['country']
        ver_status = request.GET['ver_status']
        search = searchText
        lang = language
        cout = country
        ver = ver_status
    except MultiValueDictKeyError:
        searchText = search
        language = lang
        country = cout
        ver_status = ver
    q = quote(searchText)
    language=quote(language)
    langdict = defaultdict(lambda : 'undefined')
    langdict.update({
        'en': 'English', 'ar': 'Arabic', 'bn': 'Bengali', 'cs': 'Czech', 'da': 'Danish', 'de': 'German', 'el': 'Greek',
        'es': 'Spanish', 'fa': 'Persian','fi':'Finnish','fil':'Filipino','fr':'French','he':'Hebrew','hi':'Hindi','hu':'Hungarian','id':'Indonesian','it':'Italian','ja':'Japanese','ko':'Korean','msa':'Malay','nl':'Dutch','no':'Norwegian','pl':'Polish','pt':'Portuguese','ro':'Romanian','ru':'Russian','sv':'Swedish','th':'Thai','tr':'Turkish','uk':'Ukrainian','ur':'Urdu','vi':'Vietnamese','zh-cn':'Chinese','zh-tw':'Chinese',"und":"Undefined","in":"Hindi"
    })

    #langdict= {'en':'English','ar':'Arabic','bn':'Bengali','cs':'Czech','da':'Danish','de':'German','el':'Greek','es':'Spanish','fa':'Persian','fi':'Finnish','fil':'Filipino','fr':'French','he':'Hebrew','hi':'Hindi','hu':'Hungarian','id':'Indonesian','it':'Italian','ja':'Japanese','ko':'Korean','msa':'Malay','nl':'Dutch','no':'Norwegian','pl':'Polish','pt':'Portuguese','ro':'Romanian','ru':'Russian','sv':'Swedish','th':'Thai','tr':'Turkish','uk':'Ukrainian','ur':'Urdu','vi':'Vietnamese','zh-cn':'Chinese','zh-tw':'Chinese',"und":"Undefined","in":"Hindi"}
    for code, value in langdict.items():    # for name, age in dictionary.iteritems():  (for Python 2.x)
        if language == value:
            lang=code
            break
        else:
            lang="Any"
    if lang in ['en','hi','pt']:
        lang_filter='%20AND%20'+'lang%3A('+lang+')'
    else:
        lang_filter=""

    if country in ['India', 'USA', 'Brazil']:
        country_filter='%20AND%20'+'country%3A('+country+')'
    else:
        country_filter=""

    if ver_status == "Yes" :
        ver_status_filter='%20AND%20'+'verified%3A(true)'
    elif ver_status == "No" :
        ver_status_filter='%20AND%20'+'verified%3A(false)'
    else:
        ver_status_filter=""
    #place=quote(place)
    url = 'http://18.223.109.186:8983/solr/IRF19P1/select?q=(text_en%3A('+q+')%20OR%20'+'text_hi%3A('+q+')%20OR%20'+'text_pt%3A('+q+')%20OR%20'+'full_text%3A('+q+'))'+lang_filter+country_filter+ver_status_filter+'&wt=json&indent=true&rows=500'
    print(url)
    data = urlopen(url)
    response = json.load(data)['response']
    tweets = response['docs']
    countOfTweets=response['numFound']
    print(countOfTweets)
    cnt = Counter()
    cnt1 = Counter()
    cnt2 = Counter()
    cnt3 = Counter()
    cnt4 = {"India":Counter(),"USA":Counter(),"Brazil":Counter()}
    sentiment={}
    for d in tweets:
        v1 = d['country'][0]
        v2 = d['lang'][0]
        if 'hashtags' in d:
            for v3 in d['hashtags']:
                cnt3[v3]+=1
        v4=str(parser.parse(d['tweet_date'][0]).date())
        if v1=="India": cnt4["India"][v4]+=1 
        else: cnt4["India"][v4]+=0
        if v1=="USA": cnt4["USA"][v4]+=1  
        else: cnt4["USA"][v4]+=0
        if v1=="Brazil": cnt4["Brazil"][v4]+=1 
        else: cnt4["Brazil"][v4]+=0
        cnt1[v1]+=1
        cnt2[v2]+=1
        sentiment[d['id']]=get_tweet_sentiment(d['full_text_only'][0])
    cnt5=Counter(sentiment.values())
    tweetcount = list(cnt1.values())

    langcount = list(cnt2.values())

    countries = list(cnt1.keys())

    languages = list(cnt2.keys())

    for i in range(len(languages)):
        languages[i]=langdict[languages[i]]
    t = sorted(cnt3.items(), key=lambda x:-x[1])[:10]
    hashtagcount=[b for a,b in t]
    hashtags=[a for a,b in t]

    k1=sorted(cnt4["India"].items(), key=operator.itemgetter(0))
    k2=sorted(cnt4["USA"].items(), key=operator.itemgetter(0))
    k3=sorted(cnt4["Brazil"].items(), key=operator.itemgetter(0))

    tweetdatecount={}
    tweetdates=[a for a,b in k1]
    tweetdatecount["India"]=[b for a,b in k1]
    tweetdatecount["USA"]=[b for a,b in k2]
    tweetdatecount["Brazil"]=[b for a,b in k3]

    sentiments=list(cnt5.keys())
    sentimentcounts=list(cnt5.values())
    sentimentcolormap={"neutral":"#3e95cd", "negative":"#E74C3C","positive":"#3cba9f"}
    sentimentcolors=[sentimentcolormap[i] for i in sentiments]

    name = ""
    tweet_status = False
    paginator = Paginator(tweets, 20)
    page = request.GET.get('page')
    paginateTweets = paginator.get_page(page)
    if countOfTweets > 0 :
        tweet_status = True
        name = tweets[0]['user.screen_name'][0]

        paginator = Paginator(tweets, 20)
        page = request.GET.get('page')
        paginateTweets = paginator.get_page(page)

    langauge_options=["Any","English","Hindi","Portugese"]
    country_options=["Any","India","USA","Brazil"]
    ver_status_options=["Any","Yes","No"]
    langauge_options.remove(language)
    country_options.remove(country)
    ver_status_options.remove(ver_status)
    my_dict={'tweets': tweets,
             'name': name,
             'search_term':searchText,
             'selected_lang':language,
             'selected_country':country,
             "selected_ver_status":ver_status,
             'language':langauge_options,
             'Country':country_options,
             "ver_statuses":ver_status_options,
             'countries':countries,
             'tweetcount':tweetcount,
             "langs":languages,
             "langcount":langcount,
             "trendhashtags":hashtags,
             "trendhashcounts":hashtagcount,
             "tweetdates":tweetdates,
             "india_tweetdatecount":tweetdatecount["India"],
             "usa_tweetdatecount":tweetdatecount["USA"],
             "brazil_tweetdatecount":tweetdatecount["Brazil"], 
             'paginateTweets':paginateTweets,
             "sentiments":sentiments,
             "sentimentcounts":sentimentcounts,
             "sentimentcolors":sentimentcolors,
             'tweet_status': tweet_status,
             'countOfTweets': countOfTweets }

    return render(request, 'dashboard/result.html', my_dict)


