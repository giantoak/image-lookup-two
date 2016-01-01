from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired


class UploadForm(Form):
    image_list = FileField('Your Image(s):', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], '.jpg or .png files only!')])
