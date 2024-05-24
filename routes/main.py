from flask import Blueprint, render_template, redirect, flash, url_for, session
from models import User, Course, Course_Feedback, db
from sqlalchemy import func, cast, Numeric

main_bp = Blueprint('main', __name__)


    
