from flask import Flask, render_template, session, redirect, url_for, json, request
import recurly
from pprint import pprint

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')
client = recurly.Client(app.config['RECURLY_KEY'])

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/account/')
def account_get():
    """Get the Recurly account by account_id"""
    account_id = ''
    account_id = session['account_id']
    try:
        account = client.get_account(account_id)
        return "Got Account %s" % account
    except recurly.errors.NotFoundError:
        # If the resource was not found, you may want to alert the user or
        # just return nil
        return 'Resource Not Found %s' % account_id

@app.route('/accounts')
def accounts_search():
    """Get an account's Recurly ID based on the provided 'account_code' (from email) """
    """Store the ID in the session"""
    """Redirect to /account """
    recurly_email = request.args.get('email')
    recurly_code = request.args.get('code')
    account_list = []
    accounts = client.list_accounts(limit=200, email=recurly_email).items()
    for account in accounts:
        print(account.code)
        account_list.append({"account_email": account.email, "account_id": account.id, "account_code": account.code})
    for account in account_list:
        if recurly_code == account['account_code']:
            # print("Got account %s" % account['account_id'])
            session['account_id'] = account['account_id']
            return redirect(url_for('account_get'))
            break
    else:
        """Render an failed lookup template with some direction on what to do next"""
        return json.dumps(account_list)

# TODO Add the route for updating the billing info
# @app.route('/account_update_billing')
# """Update an account's billing info with a Recurly.js token"""

