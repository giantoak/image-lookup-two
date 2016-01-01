# Views for an app that saves uploaded files into a temporary directory,
# then calls reverse image search APIs on them, then routes the results
# back.

from __future__ import print_function
from ImgSearch import get_filename_for_img, parse_google_query

# from app import app, socketio, socklogger, logger, imgsch
from app import app, logger
# from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session

from werkzeug.utils import secure_filename

from bs4 import BeautifulSoup
import simplejson as json
from pprint import pprint
import os
import sys
import requests
from threading import Timer


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def root():
    return render_template('upload_root.html')


@app.route('/upload', methods=['POST'])
def receive_upload():
    """
    Uploads all of the posted files to the server,
    saves the file names in the global session variable (g),
    and renders the client results page.

    On load, the client results page connects to a websocket, which
    triggers the API calls. Results are streamed back to the client
    as they come in.
    """
    files = request.files.getlist('file[]')
    d = dict()
    for f in files:
        try:
            sf = secure_filename(f.filename)
            # obscured_fn = imgsch.get_filename(sf)
            obscured_fn = get_filename_for_img(sf)
        except TypeError:
            print('Bad file extension in {}'.format(sf), file=sys.stderr)
            # TODO: handle bad file extensions more formally
            continue

        dest = os.path.normpath(os.path.join(app.config['UPLOAD_DIR'], obscured_fn))
        f.save(dest)
        logger.warn('saved {}'.format(dest))
        d[obscured_fn] = f.filename

    print('d has {} keys'.format(len(d)))
    session['file_dict'] = d

    all_matches = []

    for filename, actual_name in session['file_dict'].iteritems():

        fpath = os.path.normpath(os.path.join(app.config['UPLOAD_DIR'], filename))
        headers = {
            'User-Agent':
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}

        logger.debug('=== Starting r_1 ===')
        r_1 = requests.post('http://www.google.com/searchbyimage/upload',
                            files={'encoded_image': (filename, open(fpath, 'rb')), 'image_content': ''},
                            headers=headers,
                            allow_redirects=False)

        all_params = r_1.headers['Location'].split('?')[1]
        param_dict = {x.split('=')[0]: x.split('=')[1] for x in all_params.split('&')}

        logger.debug('=== Starting r_2 ===')
        logger.debug('len(param_dict) = {}'.format(len(param_dict)))
        logger.debug(param_dict)
        r_2 = requests.get('http://www.google.com/search',
                           params=param_dict,
                           headers=headers)

        bs = BeautifulSoup(r_2.text, 'lxml')
        vis_sim_href = bs.find('a', text='Visually similar images')['href']
        all_params = vis_sim_href.split('?')[1]
        param_dict = {x.split('=')[0]: x.split('=')[1] for x in all_params.split('&')}

        logger.debug('=== Starting r_3 ===')
        logger.debug('len(param_dict) = {}'.format(len(param_dict)))
        logger.debug(param_dict)
        r_3 = requests.get('http://www.google.com/search',
                           params=param_dict,
                           headers=headers,
                           allow_redirects=True)

        matches = parse_google_query(r_3.text)
        matches['filename'] = actual_name

        all_matches.append(matches)

    logger.debug('len(all_matches[0][\'results\'][:10] = {}'.format(len(all_matches[0]['results'][:10])))
    return render_template('results_gallery.html', matches=all_matches[0]['results'][:10])


# @app.route('/', methods=('GET', 'POST'))
# def root():
#     """
#     Takes a form submitting an image to the server.
#     If successful, processes the uploaded form.
#     """
#     form = UploadForm()
#     if form.validate_on_submit():
#         try:
#             sf = secure_filename(form.photo.data.filename)
#             obscured_fn = get_filename_for_img(sf)
#         except TypeError:
#             print('Bad file extension in {}'.format(sf), file=sys.stderr)
#             # TODO: handle bad file extensions more formally
#             continue
#
#         dest = os.path.normpath(os.path.join(app.config['UPLOAD_DIR'], obscured_fn))
#         form.photo.data.save(dest)
#         logger.warn('saved {}'.format(dest))
#         d = dict()
#         d[obscured_fn] = form.photo.data.filename
#
#         files = form.upload.data
#         print(files)
#         # files = request.files.getlist('file[]')
#         d = dict()
#         for f in files:
#             try:
#                 sf = secure_filename(f.filename)
#                 obscured_fn = get_filename_for_img(sf)
#             except TypeError:
#                 print('Bad file extension in {}'.format(sf), file=sys.stderr)
#                 # TODO: handle bad file extensions more formally
#                 continue
#
#             dest = os.path.normpath(os.path.join(app.config['UPLOAD_DIR'], obscured_fn))
#             f.save(dest)
#
#
#             print('d has {} keys'.format(len(d)))
#             session['file_dict'] = d
#
#         return redirect('/gallery')
#     return render_template('upload_root.html', form=form)


# @app.route('/upload')
# def receive_upload():
#     """
#     Uploads all of the posted files to the server,
#     saves the file names in the global session variable (g),
#     and renders the client results page.
#
#     On load, the client results page connects to a websocket, which
#     triggers the API calls. Results are streamed back to the client
#     as they come in.
#     """
#
#     # filename = secure_filename(form.image.data.filename)
#     # form.images.data.save('uploads/' + filename)
#
#     files = request.files.getlist('file[]')
#     d = dict()
#     for f in files:
#         try:
#             sf = secure_filename(f.filename)
#             obscured_fn = get_filename_for_img(sf)
#         except TypeError:
#             print('Bad file extension in {}'.format(sf), file=sys.stderr)
#             # TODO: handle bad file extensions more formally
#             continue
#
#         dest = os.path.normpath(os.path.join(app.config['UPLOAD_DIR'], obscured_fn))
#         f.save(dest)
#         logger.warn('saved {}'.format(dest))
#         d[obscured_fn] = f.filename
#
#     print('d has {} keys'.format(len(d)))
#     session['file_dict'] = d
#
#     return render_template('results_gallery.html')


@app.route('/_/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_DIR'], filename)


@app.route('/gallery')
def stream_results():
    logger.warn('Connected to /gallery')

    # request results from Google
    headers = {
        'User-Agent':
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    }
    # loop through objects in flask global object
    for filename, actual_name in session['file_dict'].iteritems():

        fpath = os.path.normpath(os.path.join(app.config['UPLOAD_DIR'], filename))

        r = requests.post('http://www.google.com/searchbyimage/upload',
                          headers=headers,
                          files={'encoded_image': (filename, open(fpath, 'rb')), 'image_content': ''},
                          allow_redirects=False)

        logger.warn('Requesting {}'.format(r.headers['Location']))
        r_2 = requests.get(r.headers['Location'],
                           headers=headers)

        bs = BeautifulSoup(r_2.text, 'lxml')
        logger.warn('Requesting {}'.format(bs.find('a', text='Visually similar images')['href']))
        r_3 = requests.get(bs.find('a', text='Visually similar images')['href'],
                           headers=headers)

        # result = imgsch.parse_google_query(r.text)

        print('vvvvvvvvvv')
        pprint(r_3)
        print('----')
        pprint(len(r_3.text))
        print('^^^^^^^^^^')
        result = parse_google_query(r_3.text)
        result.update({
            # 'url': google_url,
            # 'img': public_url,
            'filename': actual_name
        })

        if not r_3.ok:
            logger.warn('Google API query returned code {}'.format(r_3.code))
            continue

        logger.warn('r.ok! {}'.format(r_2.text))
        emit('result', json.dumps(result))

        # allow images to live for 5 minutes
        t = Timer(600.0, delete_file, [filename])
        t.start()


def delete_file(f):
    os.remove(os.path.join(app.config['UPLOAD_DIR'], f))
