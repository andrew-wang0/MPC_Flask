from flask import render_template


def response403(_error):
    return render_template('response/403.html')

def response404(_error):
    return render_template('response/404.html')

def response500(_error):
    return render_template('response/500.html')