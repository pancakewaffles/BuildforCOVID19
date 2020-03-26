from flask import Flask,render_template,request,Response,jsonify
import os
import json
import requests
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Environment variables
ASSISTANT_URL="https://gateway.watsonplatform.net/assistant/api"
SERVICE_URL = "https://api.au-syd.assistant.watson.cloud.ibm.com"
ASSISTANT_ID="27a27b5c-6e64-43e7-913a-ebfa7e708d22"

# IBM Cloud connection parameters
ASSISTANT_IAM_APIKEY="0ckXEHVeGhBAjrM2bVRMQIebMiX6_8cBdrJhCEcejMEX"
ASSISTANT_IAM_URL="https://api.au-syd.assistant.watson.cloud.ibm.com/instances/6ed8c814-03a6-4525-baf0-8ec4b3053493"

# Cloud Pak for Data connection parameters
#BEARER_TOKEN=
#DISABLE_SSL_VERIFICATION=false

authenticator = IAMAuthenticator(ASSISTANT_IAM_APIKEY)
assistant = AssistantV2(
    version='2020-02-05',
    authenticator = authenticator,
)
assistant.set_service_url(SERVICE_URL)
assistant.set_disable_ssl_verification(True)

debug = True

if not debug:
    import gensim

app = Flask(__name__,static_url_path='/static')

'''
Routing Stuff
Basically @app.route("/api/session") dictates what happens when the front-end calls "/api/session"
the function names are arbitrary.
'''
# This renders index.html, the main page.
@app.route("/")
def hello():
    return render_template("index.html")

# This creates a session for Watson Chatbot (on the cloud), and returns the session id.
@app.route("/api/session", methods=['GET'])
def create_session():
    response = assistant.create_session(assistant_id=ASSISTANT_ID).get_result()
    return jsonify(response)

# This creates a message and sends it to Watson Chatbot (on the cloud).
@app.route("/api/message", methods=['POST'])
def send_message():
    input_text = ""
    data = request.get_json(force=True)
    response = assistant.message(
        assistant_id=ASSISTANT_ID,
        session_id=data['session_id'],
        input={
            'message_type': 'text',
            'text': data['input']['text']
            }
        ).get_result()
    print(json.dumps(response))
    return jsonify(response)

# This dictates a search. Goes through articles and searches for relevant articles based on keywords.
@app.route("/search", methods=['GET','POST'])
def search():
    if request.method == 'POST':

        org = []

        search_string = request.form.get('search_string')  # access the data inside

        # if w2v:

        #     ##### word2vec ######

        #     #Get top 3 similar search items
        #     queries = [item[0].replace('_', '%20') for item in word2vec.most_similar(search_string, topn=3)]
        #     queries.append(search_string) #put back the original query


        #     articles = set()
        #     forums = set()



        #     for query in queries:
        #         article_parameters = {'search' : query, 'orderby' : 'relevance'}

        #         article_response = json.loads(requests.get("https://www.themix.org.uk/wp-json/wp/v2/posts?", params = article_parameters).content)
        #         for item in article_response:
        #             articles.add((item.get('title').get('rendered'), item.get('link'), item.get('featured_image_url'), item.get('excerpt').get('rendered').replace('<p>','').replace('</p>', '')))

        #         forum_response = json.loads(requests.get("https://community.themix.org.uk/search/autocomplete.json?term=" + query).content)
        #         for item in forum_response:
        #             forums.add((item.get('Title').replace('<mark>', '').replace('</mark>', ''), item.get('Url'), item.get('Summary').replace('<mark>', '').replace('</mark>', '')))

        #     articles=list(articles)
        #     forums=list(forums)
        #     articles = [list(elem) for elem in articles]
        #     forums = [list(elem) for elem in forums]

        # else:

        ###### non-word2vec ######

        query=search_string
        orgs = {1: 'abuse', 2: 'bereavement', 3: 'care', 4: 'careers', 5: 'child', 6: 'Disability', 7: 'domestic', 8: 'drugs',  9: 'relationships', 10: 'health', 11: 'housing', 12: 'legal', 13: 'mental_health', 14: 'money', 15: 'sexual', 16: 'sexuality', 17: 'self'}
        org = []
        for key, value in orgs.items():
            print(key,value)
            if value == query:

                org_response = json.loads(requests.get('https://tyt992fym8.execute-api.eu-west-2.amazonaws.com/prod/organisations?norg=1&lat=51.507351&long=-0.127758&distance=500&unit=m&>&cat=' + str(key) + '&limit=3').content.decode('utf-8')).get('results')
                for item in org_response:
                    spec_org = json.loads(requests.get('https://tyt992fym8.execute-api.eu-west-2.amazonaws.com/prod/organisations/' + str(item.get('orgid'))).content.decode('utf-8'))
                    org.append([spec_org.get('name'), spec_org.get('website'), spec_org.get('serviceoffered')])
                break

        print(query)


        articles = []
        forums = []



        article_parameters = {'search' : query, 'orderby' : 'relevance'}

        try:
            article_response = json.loads(requests.get("https://www.themix.org.uk/wp-json/wp/v2/posts?", params = article_parameters).content.decode('utf-8'))
        except:
            article_response = json.loads(requests.get("https://www.themix.org.uk/wp-json/wp/v2/posts?", params = article_parameters).content.decode('latin-1'))

        #print(article_response)
        for item in article_response:
            articles.append([item.get('title').get('rendered'), item.get('link'), item.get('featured_image_url'), item.get('excerpt').get('rendered').replace('<p>','').replace('</p>', '')])
        forum_response = json.loads(requests.get("https://community.themix.org.uk/search/autocomplete.json?term=" + query).content.decode('utf-8'))
        for item in forum_response:
            forums.append([item.get('Title').replace('<mark>', '').replace('</mark>', ''), item.get('Url'), item.get('Summary').replace('<mark>', '').replace('</mark>', '')])




    return render_template("output.html", articles=articles, forums=forums, org=org)



if __name__ == '__main__':
    #w2v=False
    # if w2v:
    #     word2vec_path = "/Users/sujay/Downloads/GoogleNews-vectors-negative300.bin.gz"
    #     word2vec = gensim.models.KeyedVectors.load_word2vec_format(word2vec_path, binary=True)


    orgs = {1: 'abuse', 2: 'bereavement', 3: 'care', 4: 'careers', 4:
'study', 5: 'child', 6: 'Disability', 7: 'domestic', 8: 'drugs', 8:
'alcohol', 9: 'relationships', 10: 'health', 11: 'housing', 12: 'legal',
13: 'mental_health', 14: 'money', 15: 'sexual', 16: 'sexuality', 17:
'self'}

    app.run()
