from flask import Blueprint, render_template, render_template_string, request, redirect, url_for, flash, session
from models import User, Course, Course_Feedback, db
from sqlalchemy import func, cast, Numeric

catalog_bp = Blueprint('catalog', __name__)
'''
@catalog_bp.route('/catalog/', methods=['GET', 'POST'])
@catalog_bp.route('/catalog', methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        min_price = request.form.get('min_price', type=int)
        max_price = request.form.get('max_price', type=int)
        filter_types = request.form.getlist('type')

        query = Course.query
        if min_price is not None:
            query = query.filter(cast(Course.price, Numeric) >= min_price)
        if max_price is not None:
            query = query.filter(cast(Course.price, Numeric) <= max_price)
        if filter_types:
            query = query.filter(Course.type.in_(filter_types))
        
        courses = query.all()
        return render_template_string('{% include "catalog_content.html" %}', courses=courses)
    
    return render_template('catalog.html', courses=Course.query.all())
'''