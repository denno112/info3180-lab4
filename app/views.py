import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm
from app.forms import UploadForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

## ------------------------- /upload route --------------------------##
@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    form = UploadForm()         ##initializing the upload form

    if request.method == 'POST' and form.validate_on_submit():      ## form validation
        f = form.upload.data  ## taking data from from 
        filename = secure_filename(f.filename)      ## securing name of filename
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))      ## joined the path to upload folder to filename
        # print("success") 

        flash('File Saved', 'success')      ## flashing message file saved
        return redirect(url_for('files'))     ## redirecting to /files route

    return render_template('upload.html', form=form)    ## rendering the upload page
## ---------------------------------------------------------------------- ##

## ------------------------------------ route for image files -----------------------##
@app.route("/uploads/<filename>")
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)
## ------------------------------------------------------------------------------------##

## -------------------------------------- /files route ------------------------------- ##
@app.route("/files")
@login_required
def files():
    list = get_uploaded_images()
    print(list)
    return render_template("files.html", list=list)
## ----------------------------------------------------------------------------------- ##

## -------------------------------------- /logout route ------------------------------- ##
@app.route('/logout')
@login_required
def logout():
    flash("You are logged out successfully")
    logout_user()
    return redirect(url_for("home"))
## ----------------------------------------------------------------------------------- ##


## -------------------------------------- /login route ------------------------------- ##
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()      ## initializing login form

    if request.method == 'POST' and form.validate_on_submit():      ## validation of form
   
        username = request.form['username']         ## taking username from form
        password = request.form['password']         ## taking password from form
      
        user = UserProfile.query.filter_by(username=username).first()       ## quering from db the username and password
      
        if user and check_password_hash(user.password, password):           ## checking if user exists and password matches with hashed passsword
            login_user(user)                                                ## login user using login_user method from flask login
            flash(user.username + " has successfully logged in")            ## flashing username with message
            return redirect(url_for("upload"))                              ## redirecting to upload page
       
        flash("User not found!")                                            ## if user not found
        return redirect(url_for("home"))                                    ##redirecting to home
    return render_template("login.html", form=form)                         ## passing form in jinga template
## ----------------------------------------------------------------------------------- ##

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

## -------------------------------- listing all filenames from upload folder -------------- ##
def get_uploaded_images():
    rootdir = os.getcwd()

    arr = []
    for subdir, dirs, files in os.walk(rootdir + "/uploads/"):
        for file in files:
            arr.append(file)

    arr.pop(0)              ## removing .gitkeep file 
    return arr              ## return list
## -----------------------------------------------------------------------------------------##

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
