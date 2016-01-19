from flask import Flask,render_template,request,make_response,redirect,url_for,session
import requests
from flask.ext.sqlalchemy import SQLAlchemy
import json
import os
from werkzeug import secure_filename
import uuid
from flask.ext.login import LoginManager,login_user,logout_user,login_required,current_user
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.bcrypt import Bcrypt


app = Flask(__name__,static_url_path="/static")
app.debug = True

# #LoginManager Instansiated
login_manager = LoginManager()

# #LoginManager Initialized
login_manager.init_app(app) 

login_manager.login_view = 'login'

# Bcrypt Config

bcrypt = Bcrypt(app)

# App Config

UPLOAD_FOLDER = '/Users/privatecaptain/freelancing/scotvision/data/img'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

SECRET_KEY = '$&^&B&*^*MN&*CDMN&*()B^&*()P^&_N*NM(P)*&D()&*^'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:badman1108@localhost/scotvision'
app.config['SECRET_KEY'] = 'faefea%$W#^TGV%$*$&^DSG'
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
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	percent_scratched = db.Column(db.Integer)

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
	campaigns = db.relationship('Campaign', backref='user', lazy='dynamic')

	email = db.Column(db.String(254), unique=True)

	
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



@login_manager.user_loader
def load_user(id):
    '''User Loader for flask-login 
    :params
     user_id -> email 
    '''
    user = User.query.get(id)
    print user.first_name,id
    if user:
        return user
    else:
        return None



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
	return redirect(url_for('dashboard'))


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
	campaigns = Campaign.query.filter_by(user_id=current_user.id)
	return render_template('dashboard.html',campaigns=campaigns)


@app.route('/create-campaign',methods=['GET','POST'])
@login_required
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
            
            if user.is_password_correct(password):
				login_user(user)
				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				return redirect(url_for('dashboard'))

        return render_template('login.html',fail=True)



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



@app.route('/signup',methods=['GET','POST'])
def register():
	
	if request.method == 'POST':

		params = request.form

		user = User()
		populate(user,params)

		# Commit db object
		db.session.add(user)
		db.session.commit()

		return redirect(url_for('login'))

	return render_template('signup.html')



@app.route('/view-campaign')
@login_required
def view_campaign():

	id = request.args.get('id')

	# Get campaign by id
	campaign = Campaign.query.get(id)

	if campaign:

		# Check User Access

		if campaign.user_id == current_user.id:
			js = generate_js(campaign)
			return render_template('view_campaign.html',campaign=campaign,js=js)

		return render_template('view_campaign.html',access=False)

	return render_template('view_campaign.html',not_found=True)


@app.route('/validate-card',methods=['POST'])
def validate_card():

	params = request.form

	id = params['id']

	if not check_lock():
		



def generate_js(campaign):
	js = render_template('gen_js.html',campaign=campaign)
	return js


def lock_session(id):
	session['lock'] = id


def remove_lock(id):
	if 'lock' in session:
		session.pop('lock',None)
	return True

def check_lock(id):
	if 'lock' in session:
		return True
	return False

def chances_left():
	if 'chances' in session:
		if session['chances'] > 0:
			session['chances'] -= 1
			return True
		return False

	return False















if __name__ == '__main__':
	app.run('0.0.0.0')

