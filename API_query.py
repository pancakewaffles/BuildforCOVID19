# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 23:51:12 2018

@author: Minh
"""
import requests
import json

query = search_string
article_parameters = {'content' : query}
articles = {}
forums = {}

article_response = json.loads(requests.get("https://www.themix.org.uk/wp-json/wp/v2/posts?", params = article_parameters).content)
for item in article_response:
    articles[item.get('title').get('rendered')] = item.get('link')
    
forum_response = json.loads(requests.get("https://community.themix.org.uk/search/autocomplete.json?term=" + query).content)
for item in forum_response:
    forums[item.get('Title').replace('<mark>', '').replace('</mark>', '')] = item.get('Url')