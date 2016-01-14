from flask import Flask,render_template,request,make_response
import requests
from flask.ext.sqlalchemy import SQLAlchemy
import json
import os
from werkzeug import secure_filename
import uuid


app = Flask(__name__,static_url_path="/static")
app.debug = True

# App Config

UPLOAD_FOLDER = '/Users/privatecaptain/scotvision/data/img'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

SECRET_KEY = '$&^&B&*^*MN&*CDMN&*()B^&*()P^&_N*NM(P)*&D()&*^'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:badman1108@localhost/scotvision'
app.config['SECRET_KEY'] = 'faefea%$W#^TGVDSG'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# DB instance init
db = SQLAlchemy(app)


# Basic Campaign Schema
class Campaign(db.Model):

	id = db.Column(db.String(254), primary_key = True)
	
	# info
	name = db.Column(db.String(254))
	type = db.Column(db.String(254))
	redirect_type = db.Column(db.String(254))

	# Stats
	total_cards = db.Column(db.Integer, default =0)
	total_winners = db.Column(db.Integer,default=0)
	winners = db.Column(db.Integer, default=0)
	losers = db.Column(db.Integer, default =0)
	scratched = db.Column(db.Integer, default= 0)
	
	# Text
	scratch_text = db.Column(db.Text)
	closed_text = db.Column(db.Text)
	
	# URLs
	redirect_url = db.Column(db.String(254))
	scratch_img_url = db.Column(db.String(254))	
	scratch_shared_img_url = db.Column(db.String(254))
	unscratch_img_url = db.Column(db.String(254))

	def __init__(self):
		self.id = str(uuid.uuid4().hex)


def allowed_filename(filename):
	return '.' in filename and \
		filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


def generate_id():
	return str(uuid.uuid4().hex)

def get_extension(filename):
	return str(filename.split('.')[1])

def upload_files(request,campaign):
	files = request.files
	for i in files:
		f = files[i]
		if f and allowed_filename(f.filename):
			filename = generate_id() + get_extension(f.filename)
			fullname = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			f.save(fullname)
			setattr(campaign,i,fullname)


def populate(campaign,params):
	for i in params:
		setattr(campaign,i,params[i])


@app.route('/',methods=['GET','POST'])
def index():
	return render_template('index.html')


@app.route('/scratch',methods=['POST'])
def scratch():
	params = request.form
	# Get Campaign ID
	try:
		campaign_id = params['id']
		result = params['result']

		# Get Campaign
		campaign = Campaign.query.get(campaign_id)
		if result == 'win':
			campaign.winners += 1
		elif result == 'lose':
			campaign.losers += 1
		else:
			pass
			# Do Nothing
		campaign.scratched += 1

		db.session.add(campaign)
		db.session.commit()
		return make_response('OK')

	except:
		return 'Invalid Request'


@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
	return render_template('dashboard.html')


@app.route('/create-campaign',methods=['GET','POST'])
def create_campaign():
	
	if request.method == 'POST':	
		params = request.form

		if params['type'] == 'competition':

			# Campaign Instance
			campaign = Campaign()
			campaign.id = generate_id()
			# Populate campaign
			populate(campaign,params)
			upload_files(request,campaign)

			db.session.add(campaign)
			db.session.commit()

		return render_template('dashboard.html')

	return render_template('campaign.html')















if __name__ == '__main__':
	app.run('0.0.0.0')