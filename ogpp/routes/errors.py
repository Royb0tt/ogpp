from flask import Blueprint, render_template, request, url_for

error_bp = Blueprint('errors', __name__)

default_back = 'home.index'


@error_bp.app_errorhandler(404)
def not_found_error(error):
    prev_page = request.args.get('next') or request.referrer or url_for(default_back)
    return render_template('errors/404.html', redirect=prev_page), 404


@error_bp.app_errorhandler(500)
def internal_error(error):
    prev_page = request.args.get('next') or request.referrer or url_for(default_back)
    return render_template('errors/500.html', redirect=prev_page), 500
