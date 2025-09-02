from flask import Blueprint, render_template

admin_routing = Blueprint('admin_routing', __name__)

@admin_routing.route('/')
def index():
    return render_template('admin/index.html', pikenetVersion=1.0)
