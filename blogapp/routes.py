from flask import redirect, render_template, flash, url_for, request, abort
from wtforms.form import Form
#from models import User, Post
from blogapp import app, db, bcrypt, mail
from blogapp.models import User, Post
from blogapp.forms import SignupForm, LoginForm, PostForm, AccountUpdateForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os
from PIL import Image
from flask_mail import Message


###########################################
###### ===ROUTES===ROUTES===ROUTES===######
###########################################


@app.route('/')
@app.route('/home/')
def home():
    ###===DISPLAY POSTS USING PAGINATION===###
    page = request.args.get('page', 1, type=int) #==GET THE 1st PAGE TO DISPLAY BLOGS==
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    return render_template('home.html',posts=posts)



@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
            email=form.email.data,
            password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash(f'Account Created for {form.username.data}','success')
        
        ##===CLEAR FORM===##
        form.username.data = ""
        form.email.data = ""
        form.password.data = ""
        return redirect(url_for('login'))
    return render_template('register.html', title='Registration', form=form)



@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful','success')
            return redirect(next_page) if next_page else redirect(url_for('new_post'))
             
        else:
            flash('Login Failed. Please check username or password!', 'danger')
            #return render_template('login.html', title='Login', form=form)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("User Logged Out")
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():

    user = User.query.get_or_404(User.id)
    return render_template('dashboard.html', title='Dashboard',user=user)


@app.route('/users')
def users():
    users = User.query.order_by(User.id)
    return render_template('users.html', title='Dashboard',users=users)

###===CREATE A FUNCTION TO SAVE PICTURE===###
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)

    picture_fn = random_hex + f_ext
    #==CREATE A FULL PATH===###
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    ####===RESIZE PICTURE===###
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    ####===SAVE PICTURE===###
    i.save(picture_path)
    return picture_fn



@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash("Account Updated Successfully",'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='images/' + current_user.image_file)
    
    return render_template('account.html', title='Account', image_file=image_file,form=form)


@app.route('/new-post', methods=['GET','POST'])
#@login_required
def new_post():
    #id = current_user.id
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
        content=form.content.data, author=current_user)
        
        db.session.add(post)
        db.session.commit()

        ##===CLEAR FORM===##
        form.title.data = ""
        form.content.data = ""

        flash('Post Successfully Created', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='New Post', form=form, legend='Create Post')


@app.route('/post/<int:post_id>', methods=['GET','POST'])
#@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title,post=post)


@app.route('/post/<int:post_id>/update', methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data

        db.session.commit()
        flash('Post Updated Successfully','success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
   

    return render_template('update_post.html', title='Update Post', form=form, post=post, legend='Update Post')



@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()

    flash('Post Deleted!','danger')

    return redirect(url_for('home'))




@app.route('/user/<string:username>')
def user_posts(username):
    ##===QUERY FOR THE USER===###
    user = User.query.filter_by(username=username).first_or_404()
    ###===DISPLAY POSTS USING PAGINATION===###
    page = request.args.get('page', 1, type=int) #==GET THE 1st PAGE TO DISPLAY BLOGS==
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    return render_template('user_posts.html', posts=posts, user=user)



###===FUNCTION TO SEND RESET EMAIL===###
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
    sender='techwavegh@gmail.com', 
    recipients=[user.email])

    msg.body = f"""

Visit the following link to reset your password:

{ url_for('reset_token', token=token, _external=True) }

Please disregard this message if you did not make the request.

Thank you.

<strong>Administrator</strong>
"""
    mail.send(msg)



@app.route('/reset-password', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Reset Email Sent. Please Check Your Mail','success')
        return redirect(url_for('login'))
    
    return render_template('reset_request.html', title='Request Password Reset', form=form)




@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)





@app.route('/test', methods=['GET','POST'])
def test(token):
    
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        
        
        flash("Password Updated Successfully!")
        return redirect(url_for('login'))

    return render_template('test.html', form=form)






