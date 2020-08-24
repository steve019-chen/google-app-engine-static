# coding: utf-8
"""
    Main Web Application for Static Sites using Flask & Python 3.7
    ----------------------------------------------------------------------------
    Deploy: sudo gcloud app deploy --project projectid --no-promote

    Run Locally (update port at the bottom if necessary):
    virtualenv -p python3 env
    source env/bin/activate
    pip install -r requirements.txt
    python main.py

    author: Karl-Heinz Müller (karlheinz@gmail.com)
"""
import datetime
import os
import xml.etree.ElementTree as ET

from flask import Flask, render_template, request, Response, abort
from flask_talisman import Talisman

from pages import documents

app = Flask(__name__, template_folder='html')
csp = {
    'default-src': ['\'self\''],
    'style-src': ['\'self\''],
    'img-src': ['\'self\'']
}

"""
    Secure dynamic server generated with nonce and all other style and javascript
    with hash 256. To create hash online use https://report-uri.com/home/hash
"""
talisman = Talisman(
    app, 
    content_security_policy=csp,
    content_security_policy_nonce_in=['style-src']
)

# GLOBAL -----------------------------------------------------------------------
"""
Load global variables declared in app.yaml
"""
APP_NAME = os.environ.get("APP_NAME")
DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
IMGIX_ROOT = os.environ.get('IMGIX_ROOT')
DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE')
BRAND = os.environ.get('BRAND')

@app.errorhandler(404)
def page_not_found(e):
    requestdata = {
        'path': request.path,
        'query': request.query_string,
        'referrer': request.headers.get("Referer")
    }
    visitor = {
        'city': request.headers.get('X-AppEngine-City'),
        'region': request.headers.get('X-AppEngine-Region'),
        'country': request.headers.get('X-AppEngine-Country'),
        'latlang': request.headers.get('X-AppEngine-Citylatlong'),
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'agent': request.headers.get('User-Agent'),
        'uuid': request.cookies.get("uuid")
    }
    header = {
        'lang': 'en',
        'brand': BRAND,
        'title': 'Oops! Page Not Found. Error 404',
        'keywords': '',
        'description': '',
        'canonical': '',
        'media': '',
        'headline': 'Oops! Looks like the page doesn\'t exist anymore.',
        'introduction': str(e),
        'breadcrumb' : ''
    }
    return render_template('/error.html',
        requestdata=requestdata,
        visitor=visitor,
        header=header), 404

@app.errorhandler(403)
def access_denied(e):
    requestdata = {
        'path': request.path,
        'query': request.query_string,
        'referrer': request.headers.get("Referer")
    }
    visitor = {
        'city': request.headers.get('X-AppEngine-City'),
        'region': request.headers.get('X-AppEngine-Region'),
        'country': request.headers.get('X-AppEngine-Country'),
        'latlang': request.headers.get('X-AppEngine-Citylatlong'),
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'agent': request.headers.get('User-Agent'),
        'uuid': request.cookies.get("uuid")
    }
    header = {
        'lang': 'en',
        'brand': BRAND,
        'title': 'Oops! Access Denied. Error 403',
        'keywords': '',
        'description': '',
        'canonical': '',
        'media': '',
        'headline': 'Oops! Access Denied. Weird.',
        'introduction': str(e),
        'breadcrumb' : ''
    }
    return render_template('/error.html',
        requestdata=requestdata,
        visitor=visitor,
        header=header), 403

@app.errorhandler(500)
def application_error(e):
    requestdata = {
        'path': request.path,
        'query': request.query_string,
        'referrer': request.headers.get("Referer")
    }
    visitor = {
        'city': request.headers.get('X-AppEngine-City'),
        'region': request.headers.get('X-AppEngine-Region'),
        'country': request.headers.get('X-AppEngine-Country'),
        'latlang': request.headers.get('X-AppEngine-Citylatlong'),
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'agent': request.headers.get('User-Agent'),
        'uuid': request.cookies.get("uuid")
    }
    header = {
        'lang': 'en',
        'brand': BRAND,
        'title': 'An Application Error has Ocurred. Error 500',
        'keywords': '',
        'description': '',
        'canonical': '',
        'media': '',
        'headline': 'Oops! An Application Error has Ocurred.',
        'introduction': str(e),
        'breadcrumb' : ''
    }
    return render_template('/error.html',
        requestdata=requestdata,
        visitor=visitor,
        header=header), 500

@app.route('/')
def homepage():
    """
        Returns homepage of the requested web site
    """
    requestdata = {
        'path': request.path,
        'query': request.query_string,
        'referrer': request.headers.get("Referer")
    }
    visitor = {
        'city': request.headers.get('X-AppEngine-City'),
        'region': request.headers.get('X-AppEngine-Region'),
        'country': request.headers.get('X-AppEngine-Country'),
        'latlang': request.headers.get('X-AppEngine-Citylatlong'),
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'agent': request.headers.get('User-Agent'),
        'uuid': request.cookies.get("uuid")
    }

    if not request.path in documents: abort(404)
    template = documents[request.path]['template']
    return render_template(template,
        requestdata=requestdata,
        visitor=visitor)

@app.route('/sitemap.xml')
def sitemap():
    '''
    Returns a sitemap for webmaster tools based on the available documents
    '''
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
    if not DOMAIN_NAME: DOMAIN_NAME = '//local'
    urlset = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for key, value in documents.items():
        url = ET.Element("url")
        changefreq = 'daily'
        if key.count('/') == 2:
            changefreq = 'weekly'
        elif key.count('/') == 3:
            changefreq = 'monthly'
        elif key.count('/') == 4:
            changefreq = 'yearly'            
        ET.SubElement(url, "loc").text = DOMAIN_NAME + key
        ET.SubElement(url, "lastmod").text = value['modified']
        ET.SubElement(url, "changefreq").text = changefreq
        ET.SubElement(url, "priority").text = value['priority']
        urlset.append(url)

    return Response(ET.tostring(urlset), mimetype='text/xml')

@app.route('/webforms/', methods=['POST'])
def webforms():
    '''
    Handles form submissions and stores the data in a gcs bucket defined in
    app.yaml
    '''
    pass

def page(**kwargs):
    """
        Deals with all page requests different than the homepage.
    """
    requestdata = {
        'path': request.path,
        'query': request.query_string,
        'referrer': request.headers.get("Referer")
    }
    visitor = {
        'city': request.headers.get('X-AppEngine-City'),
        'region': request.headers.get('X-AppEngine-Region'),
        'country': request.headers.get('X-AppEngine-Country'),
        'latlang': request.headers.get('X-AppEngine-Citylatlong'),
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'agent': request.headers.get('User-Agent'),
        'uuid': request.cookies.get("uuid")
    }

    if not request.path in documents: abort(404)
    template = documents[request.path]['template']
    return render_template(template,
        requestdata=requestdata,
        visitor=visitor)

app.add_url_rule(r'/<lvla>/', 'page', page, methods=['GET'])
app.add_url_rule(r'/<lvla>/<lvlb>/', 'page', page, methods=['GET'])
app.add_url_rule(r'/<lvla>/<lvlb>/<lvlc>/', 'page', page, methods=['GET'])
app.add_url_rule(r'/<lvla>/<lvlb>/<lvlc>/<lvld>/', 'page', page, methods=['GET'])

if __name__ == '__main__':
    """
        Used only when running the website locally. 
        Change port when necessary.
    """
    app.run(host='127.0.0.1', port=8084, debug=True)
