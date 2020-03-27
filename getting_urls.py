# wikidata sparql query to get all covid-19 pages in all wikis
# https://w.wiki/LPR

import pandas as pd 
import requests 
import re
import tldextract 
from collections import defaultdict
import json

# for a language xx and a wiki article yy you can get of external links using this query:
# https://xx.wikipedia.org/w/api.php?action=query&prop=extlinks&ellimit=max&titles=yy



def preprocess_urls(url):

    #remove the way back machine url
    #https://web.archive.org/web/20200312190124/
    url = re.sub(r"https:\/\/web\.archive\.org\/web\/\d+\/", r"", url)
    
    # todo:return None if not target language

    # domain names
    url = tldextract.extract(url).registered_domain
    return url 

def get_articles(lang, title):
    url = "https://{}.wikipedia.org/w/api.php?format=json&action=query&prop=extlinks&ellimit=max&titles={}".format(lang, title)
    r = requests.get(url = url).json()
    urls = [list(i.values())[0] for i in list(r["query"]["pages"].values())[0]["extlinks"]]
    urls = [preprocess_urls(url) for url in urls]
    return urls

df = pd.read_csv("covid_wiki_articles.csv").dropna()

lang_dict = defaultdict(list)
all_c = 0 
for c , r in enumerate(df.iterrows()):
    try:
        r = r[1]
        if c % 10 == 0 :
            print("fetching article {} of {} ".format(c, df.shape[0]))
            print("{} non-unique domains collected".format(all_c))

        urls = get_articles(r["lang"], r["name"])
        all_c += len(urls)
        
        lang_dict[r["lang"]] += urls

    except:
        print("article corrupt \t {}\t {}".format(r["name"], r["lang"]))

tmp = dict()

for k,v in lang_dict.items():
    tmp[k] = list(set([i for i in v if i is not None]))

lang_dict = tmp 

with open('covid-domains.json', 'w') as outfile:
    json.dump(lang_dict, outfile)


