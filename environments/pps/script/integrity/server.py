import os
import urllib.request
from app import app
from flask import Flask, request, redirect, jsonify, send_file
from werkzeug.utils import secure_filename
from checkIntegrity import processFile
import datetime
import time

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		resp = jsonify({'message' : 'File successfully uploaded'})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are csv'})
		resp.status_code = 400
		return resp
        
@app.route('/process-file', methods=['POST'])
def process_file():
    file = os.path.join(app.config['UPLOAD_FOLDER'], request.json['file'])
    if os.path.isfile(file):
        resp = jsonify(processFile(file))
        resp.status_code = 200
        return resp
    else:
        resp = jsonify({'message' : 'File not found'})
        resp.status_code = 400
        return resp
        
@app.route('/download-reports', methods=['GET'])
def download_reports():    
    os.system('python exports_reports.py')
    report_time = datetime.datetime.now()
    report_time_formatted = report_time.strftime('%Y%m%d%H%M%S')
    return send_file("/reports.zip", download_name=report_time_formatted + "_reports.zip", as_attachment=True)

@app.route('/delay-api/<sleep_value>', methods=['GET'])
def delay_api(sleep_value):		
    time.sleep(float(sleep_value))
    return "<html><head><title>Delay test</title></head><p>Request: %s</p><body><p>I was sleeping for %ss</p></body></html>" % (request.base_url, sleep_value)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
