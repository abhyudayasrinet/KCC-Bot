"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import request,jsonify
from FlaskDemo import app
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.corpus import stopwords
import numpy as np
import numpy.linalg as LA
import csv
import sys
import pyodbc
from heapq import nlargest

#@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/<query>',methods=['GET'])
def get_answer(query):

    data = get_sql_data()
    train_set = list(data.keys())
    #train_set.append(query)
    test_set = [query]
    stopWords = stopwords.words('english')
    vectorizer = CountVectorizer(stop_words = stopWords)
    transformer = TfidfTransformer()

    trainVectorizerArray = vectorizer.fit_transform(train_set).toarray()
    testVectorizerArray = vectorizer.transform(test_set).toarray()
    #print(testV, file=sys.stderr)
            
    transformer.fit(trainVectorizerArray)
    tfidf_train = transformer.transform(trainVectorizerArray).toarray()
    tfidf_test = transformer.transform(testVectorizerArray).toarray()
    
    prediction = {}
    i = 0
    for vector in tfidf_train:
        for testV in tfidf_test:
            cosine = cx(vector, testV)
            prediction[train_set[i]] = cosine
        i+=1
    
    #print(prediction, file=sys.stderr)
    
    chosen_values = nlargest(3, prediction, key=prediction.get)
    result = []
    for query in chosen_values:
        query_result = {}
        if(prediction[query] > 0):
            query_result["query"] = query
            query_result["answer"] = data[query]
            query_result["score"] = prediction[query]
            result.append(query_result)

    return jsonify({"result":result});


def get_sql_data():
    server = ''
    database = ''
    username = ''
    password = ''
    driver= '{SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    cursor.execute("SELECT QueryText, KCCAns from Queries")
    row = cursor.fetchone()
    data ={}
    while row:
        data[row[0]] = row[1]
        row = cursor.fetchone()
    return data

def cx(a,b):
    norm_a = LA.norm(a)
    norm_b = LA.norm(b)
    if(norm_a * norm_b != 0):
        return round(np.inner(a,b) / (norm_a * norm_b), 3)
    return 0