
from app import db
import itertools
from datetime import datetime
# import flask_login
# from sqlalchemy_mptt.mixins import BaseNestedSets

class User(db.Model):
    __tablename__ = "users"
    id = db.Column('id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(10))
    email = db.Column('email',db.String(50),unique=True , index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
    is_admin = db.Column(db.Integer, unique=False, nullable=True)
 
    def __init__(self , username ,password , email):
        self.username = username
        self.password = password
        self.email = email
        self.is_admin = 0
        self.registered_on = datetime.utcnow()
 
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return str(self.id)
 
    # def __repr__(self):
    #     return '<User %r>' % (self.username)


    def __unicode__(self):
        """Give a readable representation of an instance."""
        return '{}'.format(self.id)

    def __repr__(self):
        """Give a unambiguous representation of an instance."""
        return '<{}#{}>'.format(self.__class__.__name__, self.id)





class ProjectModel(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    desc = db.Column(db.String(1000), unique=False, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True)
    user = db.relationship('User', lazy=True,
        backref=db.backref('projects', lazy=True))

    

    created_at = db.Column('created_at' , db.DateTime)


    def __init__(self , name ,desc ,user_id ):
        self.name = name
        self.desc = desc
        self.user_id = user_id
        self.created_at = datetime.utcnow()



class ObjectTypeModel(db.Model):
    __tablename__ = 'object_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    desc = db.Column(db.String(1000), unique=False, nullable=True)
    

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True)
    user = db.relationship('User', lazy=True,
        backref=db.backref('object_types', lazy=True))



    object_type_id = db.Column(db.Integer, db.ForeignKey('object_type.id', ondelete='CASCADE'),
        nullable=True)
    childs = db.relationship("ObjectTypeModel",
                backref=db.backref('parent', remote_side=[id])
            )

    

    created_at = db.Column('created_at' , db.DateTime)


    def __init__(self , name ,desc ,user_id ,object_type_id ):
        self.name = name
        self.desc = desc
        self.object_type_id = object_type_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()


    @property
    def ancestors(self):
        if self.parent is None:
            return ()
        return itertools.chain((self.parent,), self.parent.ancestors)

    @property
    def children(self):
        if self.childs is None:
            return ()
        for ch in self.childs:
            yield itertools.chain.from_iterable((self.childs,), ch.children)



class OnjectTypeParamModel(db.Model):
    __tablename__ = 'object_type_param'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    param_type = db.Column(db.String(20), unique=False, nullable=False)
    desc = db.Column(db.String(1000), unique=False, nullable=True)

    object_type_id = db.Column(db.Integer, db.ForeignKey('object_type.id', ondelete='CASCADE'),
        nullable=True)
    object_type = db.relationship('ObjectTypeModel',lazy=True,
        backref=db.backref('parms', lazy=True))


    created_at = db.Column('created_at' , db.DateTime)


    def __init__(self ,name ,param_type ,desc ):
        self.name = name
        self.param_type = param_type
        self.desc = desc
        # self.object_type_id = object_type_id

        self.created_at = datetime.utcnow()


class ObjectTypeInstanceModel(db.Model):
    __tablename__ = 'object_type_instance'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True)
    user = db.relationship('User', lazy=True,
        backref=db.backref('object_type_instances', lazy=True))

    object_type_id = db.Column(db.Integer, db.ForeignKey('object_type.id', ondelete='CASCADE'),
        nullable=False)
    object_type = db.relationship('ObjectTypeModel', lazy=True,
        backref=db.backref('instances', lazy=True))

    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'),
        nullable=False)
    project = db.relationship('ProjectModel', lazy=True,
        backref=db.backref('instances', lazy=True))


    object_instance_id = db.Column(db.Integer, db.ForeignKey('object_type_instance.id', ondelete='CASCADE'),
        nullable=False)
    childs = db.relationship("ObjectTypeInstanceModel",
                backref=db.backref('parent', remote_side=[id])
            )

    

    created_at = db.Column('created_at' , db.DateTime)


    def __init__(self  ,user_id ,object_type_id ,object_instance_id ,project_id):
        self.object_type_id = object_type_id
        self.user_id = user_id
        self.object_instance_id = object_instance_id
        self.project_id = project_id
        self.created_at = datetime.utcnow()



class OnjectTypeInstanceParamModel(db.Model):
    __tablename__ = 'object_type_instance_param'

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.String(1000), unique=False, nullable=False)

    object_type_instance_id = db.Column(db.Integer, db.ForeignKey('object_type_instance.id', ondelete='CASCADE'),
        nullable=True)
    object_type_instance = db.relationship('ObjectTypeInstanceModel',lazy=True,
        backref=db.backref('parms', lazy=True))

    param_id = db.Column(db.Integer, db.ForeignKey('object_type_param.id', ondelete='CASCADE'),
        nullable=False)
    param = db.relationship('OnjectTypeParamModel', lazy=True,
        backref=db.backref('param_values', lazy=True))


    created_at = db.Column('created_at' , db.DateTime)


    def __init__(self ,value ,param_id):
        self.value = value
        # self.object_type_instance_id = object_type_instance_id
        self.param_id = param_id
        self.created_at = datetime.utcnow()


