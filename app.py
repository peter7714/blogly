from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = 'top_secret_secret_key'

app.app_context().push()

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def root():
    return redirect('/users')

@app.route('/users')
def users_list():
    users=User.query.order_by(User.last_name, User.first_name).all()
    return render_template('index.html', users=users)

@app.route('/users/new', methods=['GET'])
def create_user_form():
    return render_template('/users/create_user.html')

@app.route('/users/new', methods=['POST'])
def create_user():

    create_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None
    )

    db.session.add(create_user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>')
def user_details(user_id):

    user = User.query.get_or_404(user_id)

    return render_template('/users/user_details.html', user=user)

@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    
    user = User.query.get_or_404(user_id)
    return render_template('/users/edit_user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def update_user(user_id):

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect('/users')
    

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>/posts/new')
def create_post_form(user_id):
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('/posts/create_post.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def create_post(user_id):
    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist('tags')]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    create_post = Post(
        title = request.form['title'],
        content = request.form['content'],
        user = user,
        tags=tags)

    db.session.add(create_post)
    db.session.commit()

    return redirect(f'/users/{user.id}')

@app.route('/posts/<int:post_id>')
def post_details(post_id):
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('/posts/post_details.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('/posts/edit_post.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def update_post(post_id):
    post = Post.query.get_or_404('post_id')
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist('tags')]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()

    return redirect(f'/users/{post_id}')

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users/{post.user_id}')

@app.route('/tags')
def tag_list():
    tags = Tag.query.all()
    return render_template('/tags/tag_list.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def tag_details(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('/tags/tag_details.html', tag=tag)

@app.route('/tags/new')
def create_tag_form():
    posts = Post.query.all()
    return render_template('/tags/create_tag.html', posts=posts)

@app.route('/tags/new', methods=['POST'])
def create_tag():

    post_ids = [int(num) for num in request.form.getlist('posts')]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    create_tag = Tag(name=request.form['tag-name'], posts=posts)

    db.session.add(create_tag)
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:tag_id>/edit')
def edit_tag_form(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('/tags/edit_tag.html', tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def update_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['edit-tag-name']
    post_ids = [int(num) for num in request.form.getlist('posts')]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect('/tags')
