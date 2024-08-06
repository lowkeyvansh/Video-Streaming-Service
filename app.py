from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, configure_uploads, ALL
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///video_streaming.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOADED_VIDEOS_DEST'] = 'uploads/videos'
db = SQLAlchemy(app)

videos = UploadSet('videos', ALL)
configure_uploads(app, videos)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(150), nullable=False)

class VideoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=150)])
    video = FileField('Video', validators=[FileRequired(), FileAllowed(videos, 'Video files only!')])
    submit = SubmitField('Upload Video')

db.create_all()

@app.route('/')
def home():
    video_list = Video.query.all()
    return render_template('index.html', videos=video_list)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = VideoForm()
    if form.validate_on_submit():
        filename = videos.save(form.video.data)
        new_video = Video(
            title=form.title.data,
            filename=filename
        )
        db.session.add(new_video)
        db.session.commit()
        flash('Video uploaded successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('upload.html', form=form)

@app.route('/videos/<filename>')
def video(filename):
    return send_from_directory(app.config['UPLOADED_VIDEOS_DEST'], filename)

@app.route('/stream/<int:id>')
def stream(id):
    video = Video.query.get_or_404(id)
    return render_template('stream.html', video=video)

if __name__ == '__main__':
    app.run(debug=True)
