from flask import Flask,request,redirect,url_for,render_template, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import *
import math
import pymysql
pymysql.install_as_MySQLdb()
import json

app=Flask(__name__)
with open("config.json",'r')as c:
    param=json.load(c)["parameters"]
if (param['local_server']):
    app.config['SQLALCHEMY_DATABASE_URI']=param['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI']=param['production_uri']  
                     
app.config['SECRET_KEY']=param['secret_key']

db=SQLAlchemy(app)





class Contact(db.Model):
    SN=db.Column(db.Integer, primary_key=True)
    Name=db.Column(db.String(50))
    Email=db.Column(db.String(100))
    Message=db.Column(db.String(500)) 
    Date=db.Column(db.String(20))    
    
class Post(db.Model):
    Post_ID=db.Column(db.Integer,primary_key=True)
    Title=db.Column(db.String(100)) 
    Sub_Title=db.Column(db.String(50)) 
    Location=db.Column(db.String(30)) 
    Author=db.Column(db.String(50)) 
    Date=db.Column(db.String(50)) 
    Image=db.Column(db.String(100)) 
    Content=db.Column(db.String(1000)) 
    Content_1=db.Column(db.String(1000))
    Slug=db.Column(db.String(500),unique=True)

class UserDetail(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(50))
    Username=db.Column(db.String(50))
    Email=db.Column(db.String(50))
    Password=db.Column(db.String(50))

    
    
@app.route('/')
def home():
    db.session.commit()
    post_data= Post.query.all()
    n=2
    last = math.ceil(len(post_data)/n)
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    j=(page - 1)*n
    posts = post_data[ j :j + n]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)
    return render_template('index.html',posts=posts,prev=prev,next=next)
@app.route('/admin')
@login_required
def admin():
    user=current_user.Name
    if not current_user.Username=="bilzbt":
        admin_post=Post.query.filter_by(Author=user).all()
        admin_contact=Contact.query.filter_by().all()
        style="display: none;"
    else:
        admin_post=Post.query.filter_by().all()
        admin_contact=Contact.query.filter_by().all()
        style="display: block;"    
    return render_template('admin/index.html', post=admin_post,contact=admin_contact, style=style)
@app.route('/admin/edit-post/<string:Post_ID>', methods=['GET','POST'])
def admin_post(Post_ID):
    if request.method=='POST':
        title=request.form.get('title')
        sub_title=request.form.get('sub_title')
        location=request.form.get('location')
        author=current_user.Name
        date=datetime.now()
        image=request.form.get('image')
        content=request.form.get('content')
        content_2=request.form.get('content_2')
        slug=request.form.get('slug')
        if Post_ID==0:
            post=Post(Title=title, Sub_title=sub_title, Location=location, Author=author, Date=date, Image=image, Content=content, Content_1=content_2, Slug=slug)
            db.session.add(post)
            db.session.commit()
        else:
            post=Post.query.filter_by(Post_ID=Post_ID).first()
            post.Title=title   
            post.Sub_Title=sub_title
            post.Location=location
            post.Author=author
            post.Date=date
            post.Image=image
            post.Content=content
            post.Content_1=content_2
            db.session.commit()
        return redirect (url_for('admin'))    
    posts=Post.query.filter_by(Post_ID=Post_ID).first()        
    return render_template('admin/edit_post.html',posts=posts,Post_ID=Post_ID)
@app.route('/admin/delete/<string:Post_ID>',methods=['GET','POST'])
def admin_delete(Post_ID):
    post=Post.query.filter_by(Post_ID=Post_ID).first()
    db.session.delete(post)
    db.session.commit()
    return redirect (url_for('admin'))
@app.route('/admin/edit-contact/<string:SN>',methods=['GET','POST'])
def admin_contact(SN):
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        message=request.form.get('message')
        date=datetime.now()
        contact=Contact.query.filter_by(SN=SN).first() 
        contact.Name=name
        contact.Email=email
        contact.Message=message
        contact.Date=date
        db.session.commit()
        return redirect (url_for('admin'))    
    contacts=Contact.query.filter_by(SN=SN).first()        
    return render_template('admin/edit_contact.html',contacts=contacts,SN=SN)

@app.route('/admin/delete/contacts/<string:SN>',methods=['GET','POST'])
def admin_delete_contacts(SN):
    contact=Contact.query.filter_by(SN=SN).first()
    db.session.delete(contact)
    db.session.commit()
    return redirect (url_for('admin'))
    
@app.route('/post/<Slug>',methods=['GET'])
def post(Slug):
    simple_post=Post.query.filter_by(Slug=Slug).first()
    return render_template('post.html',post=simple_post)
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact',methods=['GET','POST'])                      
def contact():
    if (request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        message=request.form.get('message')
        contact=Contact(Name=name,Email=email,Message=message,Date=datetime.today().date())
        db.session.add(contact)
        db.session.commit()
    return render_template('contact.html')



login_manager=LoginManager()
login_manager.login_view='signin'
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return UserDetail.query.get(user_id)


    
@app.route('/login', methods=['GET','POST'])
def signin():
    if  request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        userdetail=UserDetail.query.filter_by(Username=username).first()
        if userdetail and userdetail.Password==password:
            login_user(userdetail)
            return redirect (url_for('admin'))   
        else:
            flash('Credentials are incorrect')  
            return redirect (url_for('signin'))      
    return render_template('signin.html')

@app.route('/logout')
@login_required
def signout():
    logout_user()
    return redirect (url_for('signin'))

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form.get('name')
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        email_data=UserDetail.query.filter_by(Email=email).first()
        username_data=UserDetail.query.filter_by(Username=username).first()
        if len(password)<10:
            flash('Password is too short')
            return redirect (url_for('signup'))
        else:
            userdetails=UserDetail(Name=name, Username=username, Email=email, Password=password)
            db.session.add(userdetails)
            db.session.commit()
        if email_data:
            flash('Email already exists')
            return redirect(url_for('signup'))
        if username_data:
            flash('Username already exists')
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/form')
def form():
    return render_template('form.html')





if __name__==('__main__'):
    with app.app_context():
        db.create_all()
        app.run(debug=True)