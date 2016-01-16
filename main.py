from flask import Flask,render_template,request,make_response,redirect,url_for
import requests
from flask.ext.sqlalchemy import SQLAlchemy
import json
import os
from werkzeug import secure_filename
import uuid
from flask.ext.login import LoginManager,login_user,logout_user,login_required,current_user
from sqlalchemy.ext.hybrid import hybrid_property



app = Flask(__name__,static_url_path="/static")
app.debug = True

# #LoginManager Instansiated
login_manager = LoginManager()

# #LoginManager Initialized
login_manager.init_app(app) 

login_manager.login_view = 'login'

# App Config

UPLOAD_FOLDER = '/Users/privatecaptain/freelancing/scotvision/data/img'
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



class User(db.Model):

	id = db.Column(db.Integer, primary_key = True, autoincrement =True)
	first_name = db.Column(db.String(254))
	last_name = db.Column(db.String(254))

	email = db.Column(db.String(254), unique=True)

	#The email of the user sans the domain for e.g. 'neil' for 'neil@nasa.gov'
	user_name = db.Column(db.String(254), unique=True)
	_password = db.Column(db.String(254))

	# Flag for session management
	authenticated = db.Column(db.Boolean, default=False)

	#Flag for email verification
	email_confirmed = db.Column(db.Boolean, default=False)

	# .password hybrid property
	@hybrid_property
	def password(self):
		return self._password

	# Hashing the password once and for all
	@password.setter
	def _set_password(self,plaintext):
		self._password = bcrypt.generate_password_hash(plaintext)

	# Password Matching
	def is_password_correct(self,plaintext):
		return bcrypt.check_password_hash(self._password, plaintext)


	# Methods required for Flask-Login to work

	def is_active(self):
		return True

	def get_id(self):
		return unicode(self.id)

	def is_authenticated(self):
		return self.authenticated

	def is_anonymous(self):
		return False


	def __repr__(self):
		return 'User : {}'.format(self.first_name)



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
@login_required
def dashboard():
	return render_template('dashboard.html')


@app.route('/create-campaign',methods=['GET','POST'])
# @login_required
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

		return redirect(url_for('dashboard'))

	return render_template('campaign.html')



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':

        params = request.form

        email = str(params['email'])
        password = params['password']
        remember = False

        if 'remember' in params:
            remember = True

        user = User.query.filter_by(email=email)
        user = user.first()

        if user:
            
            if bcrypt.check_password_hash(user.password,password):
            
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                print login_user(user,remember=remember)
                print current_user.first_name
                return redirect('/service')

        return render_template('login.html',no_acc=no_acc,wrong_pass=wrong_pass)



@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template("login.html")



@app.route('/register',methods=['GET','POST'])
def register():
	
	if request.method == 'POST':

		params = request.form

		user = User()
		populate(user,params)




if __name__ == '__main__':
	app.run('0.0.0.0')

