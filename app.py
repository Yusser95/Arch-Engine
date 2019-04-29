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

# from cloudinary.uploader import upload
# from cloudinary.utils import cloudinary_url

from datatables import ColumnDT, DataTables
from flask import  jsonify

from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.ext.declarative import DeclarativeMeta


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









# @app.before_request
# def make_session_permanent():
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(minutes=1000)



@app.route("/" , methods =["GET"])
@flask_login.login_required
def main():

	return render_template('admin.html')


@app.route("/api/documentation" , methods =["GET"])
@flask_login.login_required
def api_documentation():

	return render_template('api/documentation.html')
 




    
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
	return render_template('admin.html')





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
    columns = [
        ColumnDT(ObjectTypeModel.id),
        ColumnDT(ObjectTypeModel.name),
        ColumnDT(ObjectTypeModel.desc),

    ]

    # defining the initial query depending on your purpose
    query = db.session.query().select_from(ObjectTypeModel) #.join(User) #RecipeModel.query()
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

		obj.name = request.form.get('name')
		obj.desc = request.form.get('desc')
		obj.object_type_id = request.form.get('parent',default=None,type=int)
	

		param_types = request.form.getlist('param_types[]')
		parm_names = request.form.getlist('parm_names[]')
		param_desc = request.form.getlist('param_desc[]')
		print(param_desc)

		obj.parms.clear()
		for i in range(len(parm_names)):
			Param = OnjectTypeParamModel(name=parm_names[i],desc=param_desc[i],param_type=param_types[i])
			obj.parms.append(Param)

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
			name = request.form.get('name')
			desc = request.form.get('desc')
			object_type_id = request.form.get('parent')

			user_id = flask_login.current_user.id


			param_types = request.form.getlist('param_types[]')
			parm_names = request.form.getlist('parm_names[]')
			param_desc = request.form.getlist('param_desc[]')


			obj = ObjectTypeModel(name=name,desc=desc,user_id=user_id,object_type_id=object_type_id)

			for i in range(len(parm_names)):
				Param = OnjectTypeParamModel(name=parm_names[i],desc=param_desc[i],param_type=param_types[i])
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







# ###########      domain routes

# @app.route("/admin/recipe/kits/data", methods=['GET', "POST"])
# def recipekitsdata():

# 	params = request.args.to_dict()
# 	print(params)

# 	q= params['q']
# 	if q:
# 		kits = Meal_Kit.query.filter(Meal_Kit.name.like("%"+q+"%")).limit(50).all()
# 		db.session.commit()
# 		kits = [{"id": str(i.id), "text": i.name} for i in kits]
# 		print(kits)
# 		# kits.append({"id": q, "text": q})
# 		return jsonify(kits)

# 	kits = Meal_Kit.query.limit(50).all()
# 	db.session.commit()
# 	kits = [{"id": str(i.id), "text": i.name} for i in kits]
# 	# kits.append({"id": q, "text": q})

# 	print(kits)
# 	return jsonify(kits)



# @app.route("/admin/recipe/categories/data", methods=['GET', "POST"])
# def recipecategoriesdata():

# 	params = request.args.to_dict()
# 	print(params)

# 	q= params['q']
# 	if q:
# 		categories = CategoryModel.query.filter(CategoryModel.name.like("%"+q+"%")).limit(50).all()
# 		db.session.commit()
# 		categories = [{"id": str(i.id), "text": i.name} for i in categories]
# 		# categories.append({"id": q, "text": q})
# 		return jsonify(categories)

# 	categories = CategoryModel.query.limit(50).all()
# 	db.session.commit()
# 	categories = [{"id": str(i.id), "text": i.name} for i in categories]
# 	# categories.append({"id": q, "text": q})
# 	return jsonify(categories)


# @app.route("/admin/recipe/units/data", methods=['GET', "POST"])
# def recipeunitsdata():

# 	params = request.args.to_dict()
# 	print(params)

# 	q= params['q']
# 	if q:
# 		units = Unit.query.filter(Unit.name.like("%"+q+"%")).limit(50).all()
# 		db.session.commit()
# 		units = [{"id": i.id, "text": i.name} for i in units]
# 		# units.append({"id": q, "text": q})
# 		return jsonify(units)

# 	units = Unit.query.limit(50).all()
# 	db.session.commit()
# 	units = [{"id": i.id, "text": i.name} for i in units]
# 	# units.append({"id": q, "text": q})
# 	return jsonify(units)


# @app.route("/admin/recipe/ingredients/data", methods=['GET', "POST"])
# def recipeingredientsdata():

# 	params = request.args.to_dict()
# 	print(params)

# 	q= params['q']
# 	if q:
# 		ingredients = IngredientModel.query.filter(IngredientModel.name.like("%"+q+"%")).limit(50).all()
# 		db.session.commit()
# 		ingredients = [{"id": i.name, "text": i.name} for i in ingredients]
# 		ingredients.append({"id": q, "text": q})
# 		return jsonify(ingredients)

# 	ingredients = IngredientModel.query.limit(50).all()
# 	db.session.commit()
# 	ingredients = [{"id": i.name, "text": i.name} for i in ingredients]
# 	ingredients.append({"id": q, "text": q})
# 	return jsonify(ingredients)


# # @app.route('/admin/recipe/data')
# # @flask_login.login_required
# # def recipedata():
# #     data=RecipeModel.query.all()
# #     return jsonify(data)



# @app.route('/admin/generated_recipe/data')
# @flask_login.login_required
# def generatedrecipedata():
#     """Return server side data."""
#     # defining columns
#     columns = [
#         ColumnDT(GeneratedRecipesModel.id),
#         # ColumnDT(User.username),
#         # ColumnDT(GeneratedRecipesModel.kit_id),
#         # ColumnDT(GeneratedRecipesModel.recipe_id),
#         ColumnDT(Meal_Kit.name),
#         ColumnDT(CategoryModel.name),
        
#         ColumnDT(GeneratedRecipesModel.total_price),
#         ColumnDT(GeneratedRecipesModel.waste),
#         ColumnDT(GeneratedRecipesModel.created_at),
#         ColumnDT(ScheduleLog.name),
#         ColumnDT(Meal_Kit.id),
#         ColumnDT(RecipeModel.id),
        
#         ColumnDT(RecipeModel.name),
#         ColumnDT(CategoryModel.id)
#         # ColumnDT("""<a href="/admin/recipe/edit/{}" class="nav-link"><i class="nav-icon fa fa-edit"></i></a>""".format(RecipeModel.id)),
#         # ColumnDT("""<a  href="/admin/recipe/delete/{}" class="nav-link"><i class="nav-icon fa fa-trash"></i></a>""".format(RecipeModel.id))
#     ]

#     # defining the initial query depending on your purpose
#     query = db.session.query().select_from(GeneratedRecipesModel).join(RecipeModel,GeneratedRecipesModel.recipe).join(Meal_Kit,GeneratedRecipesModel.kit).join(ScheduleLog,GeneratedRecipesModel.job).join(CategoryModel,GeneratedRecipesModel.category) #RecipeModel.query()
    
#     # Query definition
# 	# query = db.session.query().select_from(GeneratedRecipesModel).outerjoin(Recipe, GeneratedRecipesModel.recipe_id==Recipe.id).outerjoin(Meal_Kit, GeneratedRecipesModel.kit_id==Meal_Kit.id)
    
#     db.session.commit()

#     # GET parameters
#     params = request.args.to_dict()
#     print(params)



#     # instantiating a DataTable for the query and table needed
#     rowTable = DataTables(params, query, columns)

#     # returns what is needed by DataTable
#     return jsonify(rowTable.output_result())




# @app.route("/admin/generated_recipe/more_info/<id>" , methods =["GET"])
# @flask_login.login_required
# def showgeneratedrecipemoreinfo(id):
# 	# items = GeneratedRecipesModel.query.all()
# 	# db.session.commit()
# 	items = GeneratedRecipesModel.query.get(id)

# 	return render_template('admin/generated_recipe/show_moreinfo.html',items=items)



# @app.route("/admin/generated_recipe/show" , methods =["GET"])
# @flask_login.login_required
# def showgeneratedrecipe():
# 	# items = GeneratedRecipesModel.query.all()
# 	# db.session.commit()
# 	job_id = request.args.get('job_id')
# 	job_name = None
# 	if job_id:
# 		job = ScheduleLog.query.get(job_id)
# 		if job:
# 			job_name = job.name
# 	else:
# 		job = ScheduleLog.query.order_by(ScheduleLog.created_at.desc()).first()
# 		if job:
# 			job_name = job.name



# 	return render_template('admin/generated_recipe/show.html',job_name=job_name)






# @app.route('/admin/recipe/data')
# @flask_login.login_required
# def recipedata():
#     """Return server side data"""
#     # defining columns
#     columns = [
#         ColumnDT(RecipeModel.id),
#         # ColumnDT(User.username),
#         ColumnDT(RecipeModel.name),
#         ColumnDT(RecipeModel.image),
#         ColumnDT(RecipeModel.prep_time),
#         ColumnDT(RecipeModel.cooke_time),
#         ColumnDT(RecipeModel.direction),
#         ColumnDT(RecipeModel.servings)
#         # ColumnDT("""<a href="/admin/recipe/edit/{}" class="nav-link"><i class="nav-icon fa fa-edit"></i></a>""".format(RecipeModel.id)),
#         # ColumnDT("""<a  href="/admin/recipe/delete/{}" class="nav-link"><i class="nav-icon fa fa-trash"></i></a>""".format(RecipeModel.id))
#     ]

#     # defining the initial query depending on your purpose
#     query = db.session.query().select_from(RecipeModel)#.join(User) #RecipeModel.query()
#     db.session.commit()

#     # GET parameters
#     params = request.args.to_dict()
#     print(params)



#     # instantiating a DataTable for the query and table needed
#     rowTable = DataTables(params, query, columns)

#     # returns what is needed by DataTable
#     return jsonify(rowTable.output_result())


# @app.route('/admin/recipe/data/<id>')
# @flask_login.login_required
# def recipedatabyid(id):
# 	"""Return server side data."""
# 	# defining columns
# 	columns = [
# 		ColumnDT(RecipeModel.id),
# 		# ColumnDT(User.username),
# 		ColumnDT(RecipeModel.name),
# 		ColumnDT(RecipeModel.image),
# 		ColumnDT(RecipeModel.prep_time),
# 		ColumnDT(RecipeModel.cooke_time),
# 		ColumnDT(RecipeModel.direction),
# 		ColumnDT(RecipeModel.servings)
# 		# ColumnDT("""<a href="/admin/recipe/edit/{}" class="nav-link"><i class="nav-icon fa fa-edit"></i></a>""".format(RecipeModel.id)),
# 		# ColumnDT("""<a  href="/admin/recipe/delete/{}" class="nav-link"><i class="nav-icon fa fa-trash"></i></a>""".format(RecipeModel.id))
# 	]


# 	item = Meal_Kit.query.get(id)
# 	filter =[r.id for r in item.recipes]
# 	# defining the initial query depending on your purpose
# 	query = db.session.query().select_from(RecipeModel).filter(RecipeModel.id.in_(filter))#.join(User) #RecipeModel.query()
# 	db.session.commit()

# 	# GET parameters
# 	params = request.args.to_dict()
# 	print(params)



# 	# instantiating a DataTable for the query and table needed
# 	rowTable = DataTables(params, query, columns)

# 	# returns what is needed by DataTable
# 	return jsonify(rowTable.output_result())






# @app.route("/admin/recipe/show" , methods =["GET"])
# @flask_login.login_required
# def showrecipe():
# 	# items = RecipeModel.query.limit(50).all()

# 	return render_template('admin/recipe/show.html' ,data_source="/admin/recipe/data")#,items=items)


# @app.route("/admin/recipe/show/<id>" , methods =["GET"])
# @flask_login.login_required
# def showrecipebykit(id):

# 	return render_template('admin/recipe/show.html',data_source="/admin/recipe/data/{}".format(str(id)))



# @app.route("/admin/recipe/delete/<id>" , methods =["GET"])
# @flask_login.login_required
# def deletedomain(id):
# 	print("deleted " , id)
# 	with db.session.no_autoflush:
# 		obj = RecipeModel.query.get(id)
# 		obj.kits.clear()
# 		for ing in obj.ingredients:
# 			db.session.delete(ing)
# 		db.session.commit()
# 		RecipeModel.query.filter_by(id=id).delete()
# 		db.session.commit()

# 	return redirect('/admin/recipe/show')

# @app.route("/admin/recipe/edit/<id>" , methods =["GET" , "POST"])
# @flask_login.login_required
# def editrecipe(id):
# 	_url = urlparse(request.base_url)
# 	master_url = '{0}://{1}'.format(_url.scheme, _url.netloc)
# 	# print(master_url)
# 	# edit
# 	if request.method == "POST":

# 		# with db.session.no_autoflush:

# 		obj = RecipeModel.query.get(id)



# 		obj.name = request.form.get('name')
# 		obj.prep_time = request.form.get('prep_time')
# 		obj.cooke_time = request.form.get('cooke_time')
# 		obj.servings = request.form.get('servings')
# 		obj.direction = request.form.get('direction')
# 		kits = request.form.getlist('kits[]')
# 		obj.category_id = request.form.get('category')
# 		# obj.user_id = flask_login.current_user.id
# 		if 'image' in request.files:
# 			file = request.files['image']
# 			if file:
# 				# claudera
# 				upload_result = upload(file)
# 				# obj.image = upload_result['secure_url']
# 				thumbnail_pixelate, options = cloudinary_url(
# 				upload_result['public_id'],
# 				format="jpg",
# 				crop="fill",
# 				width=300,
# 				height=200,
# 				radius=0,
# 				# effect="pixelate_faces:9",
# 				gravity="center"
# 				)
# 				obj.image = thumbnail_pixelate#.replace("c_fill_pad,g_center,h_200,r_0,w_300/","")
				

#                 # manual
# 				# filename = file.filename
# 				# path = "resources/uploads/"+obj.name.replace(" ","_").replace("#","_").replace(".","_")+"."+filename.split(".")[-1]
# 				# obj.image = "/uploads/"+obj.name.replace(" ","_").replace("#","_").replace(".","_")+"."+filename.split(".")[-1]
# 				# file.save(path)

# 		ingredients = request.form.getlist('ingredients[]')
# 		weights = request.form.getlist('weights[]')
# 		values = request.form.getlist('values[]')

# 		obj.kits.clear()
# 		for id in kits:
# 			kit = Meal_Kit.query.get(id)
# 			obj.kits.append(kit)

# 		print(ingredients,weights,values,kits)

# 		# obj.ingredients.clear()
# 		# for ing in obj.ingredients:
# 		# 	if ing.ingredient.name not in ingredients:
# 		# 		db.session.delete(ing)
# 		# 	else:
# 		# 		ingredients.remove(ing.ingredient.name)

# 		# for ing in obj.ingredients:
# 		# 	if ing.ingredient.name not in ingredients:
# 		# 		db.session.delete(ing)
# 		# 	else:
# 		# 		flag = True
# 		# 		for i in range(len(ingredients)):
# 		# 			if ing.ingredient.name == ingredients[i] and ing.unit.name == values[i] and str(ing.amount) == str(weights[i]):
# 		# 				print("found")
# 		# 				ingredients.pop(i)
# 		# 				values.pop(i)
# 		# 				weights.pop(i)
# 		# 				flag =False
# 		# 				break
# 		# 		if flag:
# 		# 			db.session.delete(ing)

# 		for ing in obj.ingredients:
# 			if ing.ingredient.name not in ingredients:
# 				db.session.delete(ing)
# 			else:
# 				flag = True
# 				for i in range(len(ingredients)):
# 					if ing.ingredient.name == ingredients[i] and ing.unit_id == values[i] and str(ing.amount) == str(weights[i]):
# 						print("found")
# 						ingredients.pop(i)
# 						values.pop(i)
# 						weights.pop(i)
# 						flag =False
# 						break
# 				if flag:
# 					db.session.delete(ing)

# 		# db.session.commit()
# 		print(ingredients,weights,values)

# 		for i in range(len(ingredients)):
# 			Ingr = Recipe_Ingr(amount=weights[i],unit_id=values[i])

# 			temp_ingr = IngredientModel.query.filter_by(name=ingredients[i]).first()
# 			if not temp_ingr:
# 				temp_ingr = IngredientModel(name=ingredients[i])
# 			Ingr.ingredient = temp_ingr


# 			# temp_unit = Unit.query.filter_by(name=values[i]).one()
# 			# temp_unit = Unit.query.get(values[i])
# 			# if not temp_unit:
# 			# 	temp_unit = Unit(name=values[i])
# 			# Ingr.unit = temp_unit


# 			obj.ingredients.append(Ingr)


# 		db.session.commit()


# 		return redirect('/admin/recipe/show')
# 	# show  one row
# 	elif request.method == "GET":
# 		item = RecipeModel.query.get(id)
# 		# print("id : ",item.kits)
# 		# categories = Meal_Kit.query.all()
# 		# ingredients = IngredientModel.query.all()
# 		# ingredients = [i.name for i in ingredients]
# 		# units = Unit.query.all()
# 		# units = [i.name for i in units]
# 		# units = db.session.query(Recipe_Ingr.unit).group_by(Recipe_Ingr.unit).all()
# 		# units = [i[0] for i in units]
# 		return render_template('/admin/recipe/edit.html',item = item)#,categories=categories,ingredients=ingredients,units=units)
# 	return "404"


# @app.route("/admin/recipe/create" , methods =["GET" , "POST"])
# @flask_login.login_required
# def createrecipe():
# 	_url = urlparse(request.base_url)
# 	master_url = '{0}://{1}'.format(_url.scheme, _url.netloc)
# 	# edit
# 	if request.method == "POST":
# 		with db.session.no_autoflush:
# 			name = request.form.get('name')
# 			prep_time = request.form.get('prep_time')
# 			cooke_time = request.form.get('cooke_time')
# 			servings = request.form.get('servings')
# 			direction = request.form.get('direction')
# 			kits = request.form.getlist('kits[]')
# 			category_id = request.form.get('category')
# 			user_id = flask_login.current_user.id
# 			image = ''
# 			if 'image' in request.files:
# 				file = request.files['image']
# 				if file:

# 					# claudira

# 					upload_result = upload(file)
# 					# obj.image = upload_result['secure_url']
# 					thumbnail_pixelate, options = cloudinary_url(
# 					upload_result['public_id'],
# 					format="jpg",
# 					crop="fill",
# 					width=300,
# 					height=200,
# 					radius=0,
# 					# effect="pixelate_faces:9",
# 					gravity="center"
# 					)
# 					image = thumbnail_pixelate#.replace("c_fill_pad,g_center,h_200,r_0,w_300/","")


# 					# manul
# 					# filename = file.filename
# 					# path = "resources/uploads/"+name.replace(" ","_").replace("#","_").replace(".","_")+"."+filename.split(".")[-1]
# 					# image = "/uploads/"+name.replace(" ","_").replace("#","_").replace(".","_")+"."+filename.split(".")[-1]
# 					# file.save(path)

# 			ingredients = request.form.getlist('ingredients[]')
# 			weights = request.form.getlist('weights[]')
# 			values = request.form.getlist('values[]')


# 			obj = RecipeModel(name=name,image=image,prep_time=prep_time,cooke_time=cooke_time,direction=direction,user_id=user_id,servings=servings,category_id=category_id)

# 			db.session.commit()
# 			for id in kits:
# 				kit = Meal_Kit.query.get(id)
# 				obj.kits.append(kit)

# 			# db.session.commit()

# 			# for i in range(len(ingredients)):
# 			# 	Ingr = Recipe_Ingr(ingr_name=ingredients[i],ingr_value=values[i],ingr_weight=weights[i])
# 			# 	obj.ingredients.append(Ingr)

# 			for i in range(len(ingredients)):
# 				Ingr = Recipe_Ingr(amount=weights[i],unit_id=values[i])

# 				temp_ingr = IngredientModel.query.filter_by(name=ingredients[i]).first()
# 				if not temp_ingr:
# 					temp_ingr = IngredientModel(name=ingredients[i])
# 				Ingr.ingredient = temp_ingr

# 				# print(values[i])
# 				# temp_unit = Unit.query.get(values[i])
# 				# if not temp_unit:
# 					# temp_unit = Unit(name=values[i])
# 				# Ingr.unit = temp_unit


# 				obj.ingredients.append(Ingr)

# 			db.session.add(obj)
# 			# db.session.flush()
# 			# db.session.refresh(obj)
# 			# domain_id = obj.id
# 			db.session.commit()


# 		return redirect('/admin/recipe/show')
# 	# show  one row
# 	elif request.method == "GET":

# 		# categories = Meal_Kit.query.all()

# 		# ingredients = IngredientModel.query.all() 
# 		# ingredients = [i.name for i in ingredients]

# 		# units = Unit.query.all()
# 		# units = [i.name for i in units]

# 		# units = db.session.query(Recipe_Ingr.unit).group_by(Recipe_Ingr.unit).all()
# 		# units = [i[0] for i in units]
# 		return render_template('/admin/recipe/create.html')#,categories=categories)#,ingredients=ingredients,units=units)
# 	return "404"





if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5001)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True, threaded=True)

