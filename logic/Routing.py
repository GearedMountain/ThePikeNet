from flask import Blueprint, render_template

basic_routing = Blueprint('basic_routing', __name__)

@basic_routing.route('/')
def index():
    return render_template('index.html', pikenetVersion=1.0)
    

