import os
import traceback
import logging
from flask import Flask, render_template, session, redirect, url_for, json, request
import recurly
from pprint import pprint
from flask_bootstrap import Bootstrap

import logging
from logdna import LogDNAHandler

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

# Flask Bootstrap extension
Bootstrap(app)

# Set-up LogDNA for logging
logdnakey = os.environ['LOGDNA_KEY']
logger = logging.getLogger('logdna')
# Disabled the level so that we can have more verbose logging send to LogDNA
# logger.setLevel(logging.INFO)
options = {}
logdna = LogDNAHandler(logdnakey, options)
root = logging.getLogger()
root.addHandler(logdna)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/accounts')
def accounts_search():
    """Gets an account's Recurly ID based on the provided 'account_code' """
    client = recurly.Client(os.environ['RECURLY_KEY'])
    recurly_email = request.args.get('email')
    recurly_code = request.args.get('code')
    account_list = []
    try: 
        accounts = client.list_accounts(limit=1, email=recurly_email).items()
        for account in accounts:
                account_list.append({"account_email": account.email, "account_id": account.id, "account_code": account.code})
        for account in account_list:
            if recurly_code == account['account_code']:

                # Log the account_id
                app.logger.info("Got account %s" % account['account_email'])

                # Store the ID in the session
                session['account_id'] = account['account_id']

            # Redirect to /account
            return redirect(url_for('account_get'))
    except recurly.errors.NotFoundError as e:
        app.logger.error('accounts_search: not found error.')
        error = 'No records found.'
        return render_template('error.html', error=error) 
    except recurly.NetworkError as e:
        app.logger.error("account_search: network error %s" %e )
        error = "We had a what appears to be temporary problem finding your records. Please try again later."
        return render_template('error.html', error=error) 
    # Catch-all if there's nothing above
    error = 'No records found.'
    return render_template('error.html', error=error) 

@app.route('/account/')
def account_get():
    """Gets a Recurly account by account_id"""
    client = recurly.Client(os.environ['RECURLY_KEY'])
    account_id = ''
    if 'account_id' in session:
        account_id = session.get('account_id')
    else:
        error = "We couldn't find your account information."
        return render_template('error.html', error=error) 
    try:
        account = client.get_account(account_id)
        app.logger.info('Showing the billing update form.')
        return render_template('account_update.html', account=account)
    except recurly.errors.NotFoundError as e:
        app.logger.error('account_get: not found error')
        error = "We couldn't find your account information."
        return render_template('error.html', error=error) 
    except recurly.NetworkError as e:
        app.logger.error("account_get: network error %s" %e )
        error = "We had a what appears to be temporary problem finding your records. Please try again later."
        return render_template('error.html', error=error) 

@app.route('/account_update_billing', methods=["POST"])
def account_update_billing():
    """Updates account's billing info"""
    client = recurly.Client(os.environ['RECURLY_KEY'])
    account_id = session.get('account_id')
    token = request.form['recurly-token']
    app.logger.info('Received a billing update form submission.')
    try:
        billing_update = {"token_id": token}
        billing = client.update_billing_info(account_id, billing_update)
        app.logger.info('Successfully updated billing info.')
        return render_template('account_update_success.html', billing=billing)
    except recurly.errors.TransactionError as e:
        app.logger.error("account_update_billing: transaction error for %s" % e )
        error = "We had a problem completing the transaction: %s" % e
        return render_template('error.html', error=error) 
    except recurly.errors.NotFoundError as e:
        app.logger.error('account_update_billing: not found error')
        error = 'We had a problem locating your record.'
        return render_template('error.html', error=error) 
    except recurly.NetworkError as e:
        app.logger.error("account_update_billing: network error %s" %e )
        error = "We had a what appears to be temporary problem finding your records. Please try again later."
        return render_template('error.html', error=error) 

@app.route("/status", methods=["GET"])
def health_check():
    app.logger.debug("debug log from /status")
    app.logger.info("info log from /status")
    app.logger.warning("warning log from /status")
    app.logger.error("error log from /status")
    app.logger.exception("exception log from /status")
    app.logger.critical("critical log from /status")
    
    # return make_response("OK", 200)
    return render_template('error.html'), 201

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    # gunicorn_logger = logging.getLogger('gunicorn.error')
    # app.logger.handlers = gunicorn_logger.handlers
    # app.logger.setLevel(gunicorn_logger.level)