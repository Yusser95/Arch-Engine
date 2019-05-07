# coding: utf-8
from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g, send_from_directory

import os
import json
from flask import Markup
import flask_login
# from flask_apscheduler import APScheduler
from sqlalchemy import desc
from operator import itemgetter
from flask import make_response
import time
from datetime import datetime, timedelta
import re
from settings import *
from urllib.parse import urlparse

import sys
# from cloudinary.uploader import upload
# from cloudinary.utils import cloudinary_url

from datatables import ColumnDT, DataTables
from flask import  jsonify
from sqlalchemy import func
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.ext.declarative import DeclarativeMeta


from ruleEngineCore import DynamicRuleEngine




# from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy
class SQLAlchemy(BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True



######.  init app
app = Flask(__name__)
app.secret_key = 'yusserbaby'
app.debug = True
cwd = os.getcwd()
# app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///'+cwd+'/resources/data.db' 
# app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get("DATABASE_URL") 
# app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql://rsonbol_foodbudg:13knBd3EvF@mysql.us.cloudlogin.co/rsonbol_foodbudg'
# app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql://root:root@localhost/flask_arch_engine'
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get("CLEARDB_DATABASE_URL")[:-15] #or 'mysql://root:root@localhost/food-budget'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 200
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.config['SQLALCHEMY_POOL_SIZE'] = 1000 

# app.config['CLOUDINARY_URL']= os.environ.get('CLOUDINARY_URL') 


db = SQLAlchemy(app)
# toolbar = DebugToolbarExtension(app)

# login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)




from models import *

# c
# db.create_all()
 
# ScheduleLog.__table__.create(db.session.bind)
# GeneratedRecipesIngrProductModel.__table__.create(db.session.bind)



def format_password(value):
	return "".join(['*' for i in value])

def format_datetime(value):
	res = '00:00:00'
	try:
		res = str(timedelta(seconds=int(value)))
	except Exception as e:
		pass
	return res

app.jinja_env.filters['password'] = format_password
app.jinja_env.filters['datetime'] = format_datetime
















@app.route("/validator/uniquename/instance" , methods =['GET',"POST"])
@flask_login.login_required
def instance_name_validator():
	response = {'valid':'true'}
	name = request.args.get('name')
	print(name)

	# item = IngredientModel.query.filter_by(name=name).first()
	item = ObjectTypeInstanceModel.query.filter(func.lower(ObjectTypeInstanceModel.name) == func.lower(name)).first()

	if item:
		response['valid'] = 'false'


	return jsonify(response)


@app.route("/validator/uniquename/object" , methods =['GET',"POST"])
@flask_login.login_required
def object_name_validator():
	response = {'valid':'true'}
	name = request.args.get('name')
	print(name)

	# item = IngredientModel.query.filter_by(name=name).first()
	item = ObjectTypeModel.query.filter(func.lower(ObjectTypeModel.name) == func.lower(name)).first()

	if item:
		response['valid'] = 'false'


	return jsonify(response)




@app.route("/validator/object/rules" , methods =['GET',"POST"])
@flask_login.login_required
def object_rules_validator():
	response = {'logs':[]}
	project_id = request.args.get('project_id')
	print(project_id)

	root_instance = ObjectTypeInstanceModel.query.filter_by(project_id=int(project_id) , object_instance_id=None).first()
	root_instances = ObjectTypeInstanceModel.query.filter_by(project_id=int(project_id)).all()
	ids = list(set([i.object_type_id for i in root_instances]))
	objects = ObjectTypeModel.query.filter(ObjectTypeModel.id.in_(ids)).all()

	rule_engine = DynamicRuleEngine()
	rule_engine.fit(objects,root_instance)
	# rule_engine.add_validation_rule("1","for i in building.Floors:\n\tprint(i.f1)")
	rule_engine.run()


	logs = rule_engine.get_logs()

	print(logs)
	if logs:
		response['logs'] = logs

	# resp = make_response(json.dumps(response))
	# resp.headers["Content-Type"]='application/json; charset=utf-8'

	return jsonify(response)





@app.route("/validator/object/rule/syntax" , methods =['GET',"POST"])
@flask_login.login_required
def object_rules_syntax_validator():
	response = {'valid':"true"}
	syntax = request.args.get('syntax')
	print(syntax)


	syntax = syntax.replace("\u2003",r"\t").replace("\t",r"\t")
	syntax = syntax.replace(r"&lt;" ,r"<").replace(r"&gt;" ,r">")
	syntax = syntax.replace(r"<br>",r"\n")
	syntax = syntax.replace(r"<p>",r"\n").replace(r"</p>","")
	syntax = syntax.replace(r"<div>",r"\n").replace(r"</div>","")
	syntax = r"{}".format(syntax)

	try:
	    temp = compile(syntax, 'fakerule', 'exec')
	    exec(temp)
	except SyntaxError as e:
		response['valid'] = "false"
		response['error'] = '[check_validation_rule][rule ({})]: '.format(rule_id)+str(e)+r"\n"+'Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text)
		print('[check_validation_rule][rule ({})]: '.format(rule_id)+str(e)+"\n"+'Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text))
	except Exception as e:
		print('[check_validation_rule][rule ({})]: '.format(rule_id)+str(e))
	except RuntimeError as e:
		print('[check_validation_rule][rule ({})]: '.format(rule_id)+str(e))

	return jsonify(response)





# @app.before_request
# def make_session_permanent():
# 	root_instance = ObjectTypeInstanceModel.query.filter_by(project_id=int(1) , object_instance_id=None).first()
# 	root_instances = ObjectTypeInstanceModel.query.filter_by(project_id=int(1)).all()
# 	ids = list(set([i.object_type_id for i in root_instances]))
# 	objects = ObjectTypeModel.query.filter(ObjectTypeModel.id.in_(ids)).all()

# 	rule_engine = DynamicRuleEngine()
# 	rule_engine.fit(objects,root_instance)
# 	# rule_engine.add_validation_rule("1","for i in building.Floors:\n\tprint(i.f1)")
# 	rule_engine.run()

# 	print(rule_engine.get_logs())

#     # session.permanent = True
#     # app.permanent_session_lifetime = timedelta(minutes=1000)



@app.route("/" , methods =["GET"])
@flask_login.login_required
def main():

	return redirect('/user/project/show')

	# return render_template('index.html')


# @app.route("/api/documentation" , methods =["GET"])
# @flask_login.login_required
# def api_documentation():

# 	return render_template('api/documentation.html')
 




    
###########      login

class UserClass(flask_login.UserMixin):
     pass

@login_manager.user_loader
def load_user(id):
	# user = UserClass() #.get(int(id))
	# user.id = id
	user = User.query.get(int(id))
	return user


# @login_manager.request_loader
# def request_loader(request):
# 	username = request.form.get('username')
# 	password = request.form.get('password')

# 	# DO NOT ever store passwords in plaintext and always compare password
# 	# hashes using constant-time comparison!
# 	user = User.query.filter_by(username=username,password=password).first()
# 	if not user:
# 		return

# 	user.is_authenticated = True
# 	return user



@app.route('/admin/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('admin/login/register.html')
    user = User(request.form['username'] , request.form['password'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    # flash('User successfully registered')
    return redirect('/admin/login')



 
@app.route('/admin/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('admin/login/login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username,password=password).first()
    db.session.commit()
    if registered_user is None:
        # flash('Username or Password is invalid' , 'error')
        return redirect('/admin/login')
    # user = UserClass(id = registered_user.id,name = username)
    flask_login.login_user(registered_user)
    # flash('Logged in successfully')
    return redirect(request.args.get('next') or '/admin')




@app.route('/admin/logout')
def logout():
    flask_login.logout_user()
    return redirect('/admin/login')



@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect('/admin/login')






@app.route('/uploads/<path:path>')
@flask_login.login_required
def send_js(path):
    return send_from_directory('resources/uploads', path)



###########      admin




@app.route("/admin" , methods =["GET"])
@flask_login.login_required
def admin():

	return redirect('/admin/object_type/show')
	# return render_template('admin.html')





###########      meal-object_typs routes



@app.route("/admin/object_type/parent/data", methods=['GET', "POST"])
def objecttypeparentdata():

	params = request.args.to_dict()
	print(params)

	q= params['q']
	if q:
		objects = ObjectTypeModel.query.filter(ObjectTypeModel.name.like("%"+q+"%")).limit(50).all()
		db.session.commit()
		objects = [{"id": i.id, "text": i.name} for i in objects]
		# objects.append({"id": q, "text": q})
		return jsonify(objects)

	objects = ObjectTypeModel.query.limit(50).all()
	db.session.commit()
	objects = [{"id": i.id, "text": i.name} for i in objects]
	# objects.append({"id": q, "text": q})
	return jsonify(objects)




def get_tree(base_page):
	dest_dict = {'key':base_page.id, 'title': base_page.name}#, 'desc': base_page.desc }
	children = base_page.childs
	if children:
		dest_dict["expanded"]= True
		dest_dict['children'] = []
		for child in children:
			dest_dict['children'].append(get_tree(child))
	return dest_dict

@app.route("/admin/object_type/parent/data/tree", methods=['GET', "POST"])
def objecttypeparentdatatree():



	# pick a root of the menu tree
	roots = ObjectTypeModel.query.filter(ObjectTypeModel.object_type_id == None).all()
	trees = []
	for root in roots:
		tree = get_tree(root)
		trees.append(tree)

	print(trees)


	# results = {"results":trees,"paginate": {"more": True}}
	# return jsonify(results)

	return jsonify(trees)



@app.route("/admin/object_type/param_types/data", methods=['GET', "POST"])
def recipekitsdata():

	params = request.args.to_dict()
	print(params)

	types = [{"id":1,"text":"string"},{"id":2,"text":"integer"},{"id":3,"text":"boolean"}]

	q= params['q']
	if q:
		# do fuzzy simmilarty
		return jsonify(types)
	return jsonify(types)


@app.route('/admin/object_type/data')
@flask_login.login_required
def object_typdata():
    """Return server side data."""
    # defining columns

    ObjectTypeModel2 = db.aliased(ObjectTypeModel)


    columns = [
        ColumnDT(ObjectTypeModel.id),
        ColumnDT(ObjectTypeModel.name),
        ColumnDT(ObjectTypeModel.desc),
        ColumnDT(ObjectTypeModel2.name)

    ]

    # defining the initial query depending on your purpose
    query = db.session.query().select_from(ObjectTypeModel).outerjoin(ObjectTypeModel2,ObjectTypeModel.parent) #RecipeModel.query()
    db.session.commit()

    # GET parameters
    params = request.args.to_dict()
    print(params)

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    # returns what is needed by DataTable
    return jsonify(rowTable.output_result())


@app.route("/admin/object_type/show" , methods =["GET"])
@flask_login.login_required
def showobject_typ():
	return render_template('admin/object_type/show.html')

@app.route("/admin/object_type/delete/<id>" , methods =["GET"])
@flask_login.login_required
def deleteobject_typ(id):
	print("deleted " , id)
	ObjectTypeModel.query.filter_by(id=id).delete()
	db.session.commit()
	return redirect('/admin/object_type/show')

@app.route("/admin/object_type/edit/<id>" , methods =["GET" , "POST"])
@flask_login.login_required
def editobject_typ(id):
	print(id)
	# edit
	if request.method == "POST":

		obj = ObjectTypeModel.query.get(id)

		obj.name = request.form.get('name').replace(" ","_")
		obj.desc = request.form.get('desc',default=None,type=str)
		obj.object_type_id = request.form.get('parent',default=None,type=int)
	
		param_ids = request.form.getlist('param_ids[]')
		param_types = request.form.getlist('param_types[]')
		parm_names = request.form.getlist('parm_names[]')
		param_desc = request.form.getlist('param_desc[]')
		print(param_desc)



		# obj.parms.clear()
		new_parms = []
		for i in range(len(parm_names)):
			# p_desc = ""
			# try:
			p_desc = param_desc[i]
			# except KeyError as e:
			# 	pass

			Param = OnjectTypeParamModel.query.get(param_ids[i])#filter_by(object_type_id=int(id),name=parm_names[i],desc=p_desc,param_type=param_types[i]).first()
			if not Param:
				Param = OnjectTypeParamModel(name=parm_names[i].replace(" ","_"),desc=p_desc,param_type=param_types[i])
				obj.parms.append(Param)
			else:
				Param.name=parm_names[i].replace(" ","_")
				Param.desc=p_desc
				Param.param_type=param_types[i]
				db.session.commit()

			new_parms.append(Param)

		for p in obj.parms:
			if p not in new_parms:
				obj.parms.remove(p)

		db.session.commit()

		return redirect('/admin/object_type/show')
	# show  one row
	elif request.method == "GET":
		item = ObjectTypeModel.query.get(id)
		return render_template('/admin/object_type/edit.html',item = item)
	return "404"

@app.route("/admin/object_type/create" , methods =["GET" , "POST"])
@flask_login.login_required
def create_object_type():
	_url = urlparse(request.base_url)
	master_url = '{0}://{1}'.format(_url.scheme, _url.netloc)
	# edit
	if request.method == "POST":
		with db.session.no_autoflush:
			name = request.form.get('name').replace(" ","_")
			desc = request.form.get('desc',default=None,type=str)
			object_type_id = request.form.get('parent')

			user_id = flask_login.current_user.id


			param_types = request.form.getlist('param_types[]')
			parm_names = request.form.getlist('parm_names[]')
			param_desc = request.form.getlist('param_desc[]')


			obj = ObjectTypeModel(name=name.replace(" ","_"),desc=desc,user_id=user_id,object_type_id=object_type_id)

			for i in range(len(parm_names)):
				p_desc = ""
				try:
					p_desc = param_desc[i]
				except KeyError as e:
					pass
				Param = OnjectTypeParamModel(name=parm_names[i].replace(" ","_"),desc=p_desc,param_type=param_types[i])
				obj.parms.append(Param)

			db.session.add(obj)
			# db.session.flush()
			# db.session.refresh(obj)
			# domain_id = obj.id
			db.session.commit()


		return redirect('/admin/object_type/show')
	# show  one row
	elif request.method == "GET":
		return render_template('/admin/object_type/create.html')
	return "404"





@app.route("/admin/object_type/rules/edit/<id>" , methods =["GET" , "POST"])
@flask_login.login_required
def editobject_type_rules(id):
	print(id)
	# edit
	if request.method == "POST":

		obj = ObjectTypeModel.query.get(id)

		param_ids = request.form.getlist('param_ids[]')
		parm_names = request.form.getlist('parm_names[]')
		param_desc = request.form.getlist('param_desc[]')
		print(param_ids)



		# obj.rules.clear()
		new_rules = []
		for i in range(len(parm_names)):
			# p_desc = ""
			# try:
			p_desc = param_desc[i]
			
			# except KeyError as e:
			# 	pass

			Rule = OnjectTypeRuleModel.query.get(param_ids[i])
			if not Rule:
				Rule = OnjectTypeRuleModel(name=parm_names[i],syntax=p_desc)
				obj.rules.append(Rule)
			else:
				Rule.name=parm_names[i]
				Rule.syntax=p_desc
				db.session.commit()


			new_rules.append(Rule)

		for p in obj.rules:
			if p not in new_rules:
				obj.rules.remove(p)

		db.session.commit()

		return redirect('/admin/object_type/show')
	# show  one row
	elif request.method == "GET":
		item = ObjectTypeModel.query.get(id)
		return render_template('/admin/object_type/rules_page.html',item = item)
	return "404"

















###########      domain routes

@app.route("/admin/user/show" , methods =["GET"])
@flask_login.login_required
def showuser():
	# print(flask_login.current_user.id)

	items = User.query.all()
	db.session.commit()
	return render_template('admin/user/show.html',items=items)

@app.route("/admin/user/delete/<id>" , methods =["GET"])
@flask_login.login_required
def deleteuser(id):
	print("deleted " , id)
	User.query.filter_by(id=id).delete()
	db.session.commit()
	return redirect('/admin/user/show')

@app.route("/admin/user/edit/<id>" , methods =["GET" , "POST"])
@flask_login.login_required
def edituser(id):
	print(id)
	# edit
	if request.method == "POST":
		username = request.form.get('username')
		password = request.form.get('password')
		email = request.form.get('email')

		obj = User.query.get(id)


		obj.username = username
		obj.password = password
		obj.email = email
		db.session.commit()

		return redirect('/admin/user/show')
	# show  one row
	elif request.method == "GET":

		item = User.query.get(id)
		db.session.commit()
		return render_template('/admin/user/edit.html',item = item)
	return "404"


@app.route("/admin/user/create" , methods =["GET" , "POST"])
@flask_login.login_required
def createuser():
	# edit
	if request.method == "POST":
		username = request.form.get('username')
		password = request.form.get('password')
		email = request.form.get('email')
		user_id = flask_login.current_user.id

		obj = User(username=username,email=email,password=password)
		db.session.add(obj)
		db.session.flush()
		db.session.refresh(obj)
		user_id = obj.id
		db.session.commit()


		# dd = datetime.now() + timedelta(seconds=3)
		# scheduler.add_job(reindex_data, 'date',run_date=dd,id="reindex_"+str(user_id), kwargs={'user':ch_word,'user_id':user_id})

		# reindex_data(ch_word,user_id)

		return redirect('/admin/user/show')
	# show  one row
	elif request.method == "GET":
		return render_template('/admin/user/create.html')
	return "404"






















@app.route('/user/project/data')
@flask_login.login_required
def projectdata():
    """Return server side data."""
    # defining columns

    # ObjectTypeModel2 = db.aliased(ObjectTypeModel)


    columns = [
        ColumnDT(ProjectModel.id),
        ColumnDT(ProjectModel.name),
        ColumnDT(ProjectModel.desc),
        ColumnDT(ProjectModel.created_at)

    ]

    # defining the initial query depending on your purpose
    query = db.session.query().select_from(ProjectModel)#.outerjoin(ObjectTypeModel2,ObjectTypeModel.parent) #RecipeModel.query()
    db.session.commit()

    # GET parameters
    params = request.args.to_dict()
    print(params)

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)

    # returns what is needed by DataTable
    return jsonify(rowTable.output_result())

@app.route("/user/project/show" , methods =["GET"])
@flask_login.login_required
def showproject():
	# edit
	return render_template('/user/project/show.html')

@app.route("/user/project/delete/<id>" , methods =["GET"])
@flask_login.login_required
def deleteproject(id):
	print("deleted " , id)
	ProjectModel.query.filter_by(id=id).delete()
	db.session.commit()
	return redirect('/user/project/show')

@app.route("/user/project/create" , methods =["GET" , "POST"])
@flask_login.login_required
def createproject():
	# edit
	if request.method == "POST":
		name = request.form.get('name')
		desc = request.form.get('desc',default=None,type=str)
		# root_object_id = request.form.get('parent')
		user_id = flask_login.current_user.id
		
		obj = ProjectModel(name=name,desc=desc,user_id=user_id)

		db.session.add(obj)
		db.session.flush()
		db.session.refresh(obj)
		project_id = obj.id
		db.session.commit()

		return redirect('/user/project/{}/instance/show/-1'.format(str(project_id)))

	# show  one row
	elif request.method == "GET":
		return render_template('/user/project/create.html')
	return "404"


@app.route("/user/project/edit/<id>" , methods =["GET" , "POST"])
@flask_login.login_required
def editproject(id):
	# edit
	if request.method == "POST":
		obj = ProjectModel.query.get(id)

		obj.name = request.form.get('name')
		obj.desc = request.form.get('desc',default=None,type=str)

		db.session.commit()

		return redirect('/user/project/show')

	# show  one row
	elif request.method == "GET":
		item = ProjectModel.query.get(id)
		return render_template('/user/project/edit.html',item=item)
	return "404"

























@app.route("/user/object_type/children/data/<i_id>", methods=['GET', "POST"])
def objecttypeinstancechildsdata(i_id):

	params = request.args.to_dict()
	print(params)


	if i_id == '-1':
		q= params['q']
		if q:
			objects = ObjectTypeModel.query.filter(ObjectTypeModel.name.like("%"+q+"%")).limit(50).all()
			objects = [{"id": i.id, "text": i.name} for i in objects]
			# objects.append({"id": q, "text": q})
			return jsonify(objects)

		objects = ObjectTypeModel.query.limit(50).all()
		objects = [{"id": i.id, "text": i.name} for i in objects]
		# objects.append({"id": q, "text": q})
		return jsonify(objects)

	else:
		instance = ObjectTypeInstanceModel.query.get(i_id)
		objects_children_ids = [i.id for i in instance.object_type.childs]
		q= params['q']
		if q:
			objects = ObjectTypeModel.query.filter(ObjectTypeModel.id.in_(objects_children_ids),ObjectTypeModel.name.like("%"+q+"%")).limit(50).all()
			objects = [{"id": i.id, "text": i.name} for i in objects]
			# objects.append({"id": q, "text": q})
			return jsonify(objects)

		objects = ObjectTypeModel.query.filter(ObjectTypeModel.id.in_(objects_children_ids)).limit(50).all()
		objects = [{"id": i.id, "text": i.name} for i in objects]
		# objects.append({"id": q, "text": q})
		return jsonify(objects)


def get_instance_tree(base_page):
	dest_dict = {'key':base_page.id, 'title':"{} ({})".format(base_page.name, base_page.object_type.name)}#, 'desc': base_page.desc }
	children = base_page.childs
	if children:
		dest_dict["expanded"]= True
		dest_dict['children'] = []
		for child in children:
			dest_dict['children'].append(get_instance_tree(child))
	return dest_dict

@app.route("/user/instance/data/tree/<id>", methods=['GET', "POST"])
def objecttypeparentdatatreeid(id):

	# pick a root of the menu tree
	root = ObjectTypeInstanceModel.query.get(id) #.filter(ObjectTypeModel.object_type_id == None).all()
	trees = []
	if root:
		tree = get_instance_tree(root)
		trees.append(tree)

	return jsonify(trees)



@app.route("/user/project/<p_id>/instance/show/<i_id>" , methods =["GET"])
@flask_login.login_required
def showprojectinstance(p_id,i_id):
	print(p_id)
	project = ProjectModel.query.get(p_id)
	root_instance = ObjectTypeInstanceModel.query.filter_by(project_id=int(p_id) , object_instance_id=None).first()
	if root_instance:
		if i_id == '-1':
			i_id = root_instance.id
			selected_instance = root_instance
		else:
			selected_instance = ObjectTypeInstanceModel.query.get(i_id)
		return render_template('/user/object_instance/show.html',item=selected_instance, i_id=str(i_id), project=project, instance_data_source="/user/instance/data/tree/{}".format(str(root_instance.id)))

	return redirect('/user/project/{}/instance/create/-1'.format(str(p_id)))


@app.route("/user/project/<p_id>/instance/delete/<i_id>" , methods =["GET"])
@flask_login.login_required
def deleteprojectinstance(p_id,i_id):
	print("deleted " , i_id)
	ObjectTypeInstanceModel.query.filter_by(id=i_id).delete()
	db.session.commit()
	return redirect('/user/project/{}/instance/show/{}'.format(str(p_id),str("-1")))#i_id)))


@app.route("/user/project/<p_id>/instance/create/<i_id>" , methods =["GET" , "POST"])
@flask_login.login_required
def createprojectinstance(p_id , i_id):
	# edit
	if request.method == "POST":
		object_type_id = request.form.get('object_type_id',type=int)
		name = request.form.get('name',type=str).replace(" ","_")
		# project_id = request.form.get('project_id')
		# desc = request.form.get('desc',default=None,type=str)
		project_id = int(p_id)
		object_instance_id = None
		if i_id != '-1':
			object_instance_id = int(i_id)
		user_id = flask_login.current_user.id
		
		obj = ObjectTypeInstanceModel(name=name.replace(" ","_"),object_type_id=object_type_id,project_id=project_id,object_instance_id=object_instance_id,user_id=user_id)

		parms_ids = request.form.getlist('parms_ids[]')
		parms_values = request.form.getlist('parms_values[]')

		# print(parms_ids,parms_values)


		for i in range(len(parms_ids)):
			Param = OnjectTypeInstanceParamModel(value=parms_values[i],param_id=parms_ids[i])
			obj.parms.append(Param)

		db.session.add(obj)
		db.session.flush()
		db.session.refresh(obj)
		instance_id = obj.id
		db.session.commit()

		return redirect('/user/project/{}/instance/show/{}'.format(str(p_id),str(instance_id)))

	# show  one row
	elif request.method == "GET":
		project = ProjectModel.query.get(p_id)
		root_instance = ObjectTypeInstanceModel.query.filter_by(project_id=p_id , object_instance_id=None).first()
		rt_id = -1
		if root_instance:
			rt_id = root_instance.id
		return render_template('/user/object_instance/create.html',i_id=str(i_id), project=project, instance_data_source="/user/instance/data/tree/{}".format(str(rt_id)) ,objects_data_source="/user/object_type/children/data/{}".format(str(i_id)))

	return "404"



@app.route("/user/project/<p_id>/instance/edit/<i_id>" , methods =["GET" , "POST"])
@flask_login.login_required
def editprojectinstance(p_id , i_id):
	# edit
	if request.method == "POST":



		parms_ids = request.form.getlist('parms_ids[]')
		parms_values = request.form.getlist('parms_values[]')

		obj = ObjectTypeInstanceModel.query.get(int(i_id))

		obj.name = request.form.get('name',type=str).replace(" ","_")


		obj.parms.clear()
		for i in range(len(parms_ids)):
			Param = OnjectTypeInstanceParamModel(value=parms_values[i],param_id=parms_ids[i])
			obj.parms.append(Param)


		
		db.session.commit()

		instance_id = obj.id

		return redirect('/user/project/{}/instance/show/{}'.format(str(p_id),str(instance_id)))

	# show  one row
	elif request.method == "GET":
		item = ObjectTypeInstanceModel.query.get(i_id)
		project = ProjectModel.query.get(p_id)
		root_instance = ObjectTypeInstanceModel.query.filter_by(project_id=p_id , object_instance_id=None).first()
		rt_id = -1
		if root_instance:
			rt_id = root_instance.id
		return render_template('/user/object_instance/edit.html',i_id=str(i_id), item=item, project=project, instance_data_source="/user/instance/data/tree/{}".format(str(rt_id)) ,objects_data_source="/user/object_type/children/data/{}".format(str(i_id)))

	return "404"


@app.route('/user/instance/parms_form' , methods =["GET" , "POST"])
@flask_login.login_required
def instance_parms_form():
	# edit
	if request.method == "POST":

		object_id = request.json.get('object_id')
		item = ObjectTypeModel.query.get(object_id)
		return render_template('/user/object_instance/parms_form.html',item=item)
	return "404"

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5001)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True, threaded=True)

