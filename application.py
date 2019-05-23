from dbConnection import createAlert, getAlertLog

import adal
import flask
import uuid
import requests
import config
from flask import request
import pandas as pd


app = flask.Flask(__name__)
app.debug = True
app.secret_key = 'development'

PORT = 5000  
AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/' + config.TENANT
#REDIRECT_URI = 'http://localhost:{}/getAToken'.format(PORT)
REDIRECT_URI = 'https://poc-hot-path-analytics.azurewebsites.net/getAToken'
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')


@app.route("/")
def main():
    #login_url = 'http://localhost:{}/login'.format(PORT)
    login_url = 'https://poc-hot-path-analytics.azurewebsites.net/login'
    resp = flask.Response(status=307)
    resp.headers['location'] = login_url
    return resp


@app.route("/login")
def login():
    auth_state = str(uuid.uuid4())
    flask.session['state'] = auth_state
    authorization_url = TEMPLATE_AUTHZ_URL.format(
        config.TENANT,
        config.CLIENT_ID,
        REDIRECT_URI,
        auth_state,
        config.RESOURCE)
    resp = flask.Response(status=307)
    resp.headers['location'] = authorization_url
    return resp


@app.route("/getAToken")
def main_logic():
    code = flask.request.args['code']
    state = flask.request.args['state']
    if state != flask.session['state']:
        raise ValueError("State does not match")
    auth_context = adal.AuthenticationContext(AUTHORITY_URL)
    token_response = auth_context.acquire_token_with_authorization_code(code, REDIRECT_URI, config.RESOURCE,
                                                                        config.CLIENT_ID, config.CLIENT_SECRET)

    flask.session['access_token'] = token_response['accessToken']

    return flask.redirect('/graphcall')


@app.route('/graphcall')
def graphcall():
    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    endpoint = config.RESOURCE + '/' + config.API_VERSION + '/me/'
    http_headers = {'Authorization': 'Bearer ' + flask.session.get('access_token'),
                    'User-Agent': 'adal-python-sample',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid.uuid4())}
    graph_data = requests.get(endpoint, headers=http_headers, stream=False).json()
    df = getAlertLog()
    print(graph_data)
    #return flask.render_template('display_graph_info.html', graph_data=graph_data)
    return flask.render_template('alert.html', alertLog=df.to_html(), graph_data=graph_data, userPrincipalName = graph_data['userPrincipalName'], displayName = graph_data['displayName'])

@app.route('/graphcall', methods=['POST'])
def my_form_post():
    temperature = request.form['temperature_value']
    phone = request.form['phone']
    email = request.form['email']
    displayName = request.form['displayName']
    processed_text = 'Alert is set to when temperature >= ' + temperature + ' for  ' + phone 
    frequency = 'daily'
    parameter = 'temperature'
    condition = 'gte'
    createAlert(str(phone), str(frequency), str(parameter), str(condition), temperature, str(email))
    return processed_text
    #return flask.render_template('success.html', displayName=displayName, message=processed_text)



if __name__ == "__main__":
    app.run()
