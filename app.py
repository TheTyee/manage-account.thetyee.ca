from flask import Flask, render_template, session, redirect, url_for, json, request
import recurly
from pprint import pprint
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

app.config.from_pyfile('settings.cfg')
client = recurly.Client(app.config['RECURLY_KEY'])

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/account/')
def account_get():
    """Gets a Recurly account by account_id"""
    if 'account_id' in session:
        #TODO Handle recurly.NetworkError: [Errno 54] Connection reset by peer
        account_id = session.get('account_id')
    else:
        account_id = '0'
    try:
        account = client.get_account(account_id)
        #return "Got Account %s" % account
        # TODO only for debugging:
        # print(account)
        return render_template('account_update.html', account=account)
    except recurly.errors.NotFoundError:
        error = ''
        # If the resource was not found, you may want to alert the user or
        # just return nil
        #return 'Resource Not Found %s' % account_id
        return render_template('error.html', error=error) 

@app.route('/accounts')
def accounts_search():
    """Gets an account's Recurly ID based on the provided 'account_code' """
    recurly_email = request.args.get('email')
    recurly_code = request.args.get('code')
    account_list = []
    accounts = client.list_accounts(limit=1, email=recurly_email).items()
    for account in accounts:
        # print(account.code)
        account_list.append({"account_email": account.email, "account_id": account.id, "account_code": account.code})
    for account in account_list:
        if recurly_code == account['account_code']:
            # TODO only print when debugging
            # print("Got account %s" % account['account_id'])
            # Store the ID in the session
            session['account_id'] = account['account_id']
            # Redirect to /account
            return redirect(url_for('account_get'))
            break
    else:
        # TODO Render an failed lookup template with some direction on what to do next
        #return json.dumps(account_list)
        return render_template('error.html') 

@app.route('/account_update_billing', methods=["POST"])
def account_update_billing():
    """Updates account's billing info"""
    account_id = session.get('account_id')
    token = request.form['recurly-token']
    try:
        billing_update = {"token_id": token}
        billing = client.update_billing_info(account_id, billing_update)
        # TODO only print when debugging
        #print("Updated BillingInfo %s" % billing)
        return render_template('account_update_success.html', billing=billing)
    except recurly.errors.ValidationError as e:
        # If the request was invalid, you may want to tell your user
        # why. You can find the invalid params and reasons in e.error.params
        # TODO log these errors
        #print("ValidationError: %s" % e.error.message)
        #print(e.error.params)
        return render_template('error.html', error=e) 


