g={}
class BaseClass(object):
def __init__(self, classtype):
self._type = classtype

def ClassFactory(name, argnames=[], BaseClass=BaseClass):
def __init__(self, **kwargs):
setattr(self, "logs", [])
for key, value in kwargs.items():
if argnames:
if key not in argnames:
raise TypeError("Argument %s not valid for %s" % (key, self.__class__.__name__))
setattr(self, key, value)
BaseClass.__init__(self, name)
def check_rules(self):
try:
base=self.logging+self.att_str+self.rule_str
codeobj = compile(base, 'fakemodule', 'exec')
self.env = self.exec_env
global g
self.env['parent']=g.get(self.parent)
exec(codeobj,self.env,self.env)
self.logs.extend(self.env.get('inner_logs'))
except SyntaxError as e:
self.logs.append('[error][check_rules][SyntaxError]: '+str(e)+' Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text))
self.logs.extend(x.data)
return False
except Exception as e:
self.logs.append('[error][check_rules][Exception]: '+str(e))
self.logs.extend(x.data)
return False
except RuntimeError as e:
self.logs.append('[error][check_rules][RuntimeError]: '+str(e))
self.logs.extend(x.data)
return False
def set_parent(self):
global g
self.parent=g.get(self.parent)
newclass = type(name, (BaseClass,),{"__init__": __init__,"check_rules":check_rules,"set_parent":set_parent})
return newclass
logs=[]
def add_to_log(error):
logs.append(error)
Room = ClassFactory('Room')
floor = ClassFactory('floor')
Building = ClassFactory('Building')
f3 = floor(Name = '12'  ,  parent = 'test1'  ,  Rooms = []  ,  att_str = "\nName = '12'\nparent = 'test1'\nRooms = []\n\n",logging = '\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n',exec_env = {},rule_str = "\n\ntry:\n\tif parent:\n\t\tprint(parent.Occupant_Load)\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (test for parent - floor)]: '+str(e))\n\n")
g['f3']=f3
f2 = floor(Name = '17'  ,  parent = 'test1'  ,  Rooms = []  ,  att_str = "\nName = '17'\nparent = 'test1'\nRooms = []\n\n",logging = '\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n',exec_env = {},rule_str = "\n\ntry:\n\tif parent:\n\t\tprint(parent.Occupant_Load)\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (test for parent - floor)]: '+str(e))\n\n")
g['f2']=f2
r44 = Room(name = 'room2'  ,  Complied_code = 'IBC code'  ,  room_type = 'foyer'  ,  parent = 'f1'  ,  att_str = "\nname = 'room2'\nComplied_code = 'IBC code'\nroom_type = 'foyer'\nparent = 'f1'\n\n",logging = '\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n',exec_env = {},rule_str = "\n\ntry:\n\tif parent:\n\t\tprint(parent.Name)\n\telse:\n\t\tprint ('parent not valid')\n\t\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (402-Covered mall and open mall buildings)]: '+str(e))\n\n")
g['r44']=r44
f1 = floor(Name = 'ee'  ,  parent = 'test1'  ,  Rooms = [r44]  ,  r44 = r44  ,  att_str = "\nName = 'ee'\nparent = 'test1'\nRooms = [r44]\nr44 = r44\n\n",logging = '\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n',exec_env = {'r44' : r44},rule_str = "\n\ntry:\n\tif parent:\n\t\tprint(parent.Occupant_Load)\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (test for parent - floor)]: '+str(e))\n\n")
g['f1']=f1
Room1 = Room(name = '1'  ,  Complied_code = '500'  ,  room_type = '1'  ,  parent = 'ff'  ,  att_str = "\nname = '1'\nComplied_code = '500'\nroom_type = '1'\nparent = 'ff'\n\n",logging = '\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n',exec_env = {},rule_str = "\n\ntry:\n\tif parent:\n\t\tprint(parent.Name)\n\telse:\n\t\tprint ('parent not valid')\n\t\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (402-Covered mall and open mall buildings)]: '+str(e))\n\n")
g['Room1']=Room1
ff = floor(Name = '56563222'  ,  parent = 'test1'  ,  Rooms = [Room1]  ,  Room1 = Room1  ,  att_str = "\nName = '56563222'\nparent = 'test1'\nRooms = [Room1]\nRoom1 = Room1\n\n",logging = '\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n',exec_env = {'Room1' : Room1},rule_str = "\n\ntry:\n\tif parent:\n\t\tprint(parent.Occupant_Load)\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (test for parent - floor)]: '+str(e))\n\n")
g['ff']=ff
test1 = Building(Height = 123669  ,  No_of_floors = 1  ,  Occupant_Load = '3369'  ,  Building_Type = '1'  ,  ID = 1  ,  parent = ''  ,  Name = None  ,  floors = [ff,f1,f2,f3]  ,  ff = ff  ,  f1 = f1  ,  f2 = f2  ,  f3 = f3  ,  att_str = "\nHeight = 123669\nNo_of_floors = 1\nOccupant_Load = '3369'\nBuilding_Type = '1'\nID = 1\nparent = ''\nName = None\nfloors = [ff,f1,f2,f3]\nff = ff\nf1 = f1\nf2 = f2\nf3 = f3\n\n",logging = '\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n',exec_env = {'ff' : ff,'f1' : f1,'f2' : f2,'f3' : f3},rule_str = "\n\ntry:\n\ti = 1\n\tx = 'Covered Mall'\n\t\n\t\n\tif Building_Type == x and len(floors) > 2 :\n\t\t\tprint('building:{}  type is {} and accordingly 402 is applicable'.format(ID,Building_Type))\n\telse :\n\t\t\tprint('chapter 402 is not applicable')\n\t\n\t\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (output  parameters)]: '+str(e))\n\ntry:\n\tprint('rule : r3 , Building : {}'.format(Name))\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (r3)]: '+str(e))\n\ntry:\n\tfor f in floors:\n\t\tif f.Name:\n\t\t\tprint('rule 66r5 , Building : {}, floors : {}'.format(Name,f.Name))\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (r5)]: '+str(e))\n\ntry:\n\tfor f in floors:\n\t\tif len(f.Rooms) > 0:\n\t\t\tfor r in f.Rooms:\n\t\t\t\tprint('rule : r6 , Building : {}, floors : {} ,room : {}'.format(Name,f.Name,r.Name))\n\t\t\t\t\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (r6)]: '+str(e))\n\ntry:\n\tprint('rule : r7 ,number of floors : {}'.format(str(len(floors))))\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (r7)]: '+str(e))\n\ntry:\n\tif int(Height) > 500 :\n\t\tprint('Height most be less or equal &nbsp;500')\n\telse:\n\t\tprint('Height is ok')\n\t\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (r8)]: '+str(e))\n\ntry:\n\tif parent:\n\t\tprint(parent.Name)\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (parent_test)]: '+str(e))\n\ntry:\n\tif floors:\n\t\tprint(floors[0].parent.Name)\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule (child_parent_test)]: '+str(e))\n\n")
g['test1']=test1
f3.set_parent()

f2.set_parent()

r44.set_parent()

f1.set_parent()

Room1.set_parent()

ff.set_parent()

test1.set_parent()
f3.check_rules()
logs.extend(f3.logs)

f2.check_rules()
logs.extend(f2.logs)

r44.check_rules()
logs.extend(r44.logs)

f1.check_rules()
logs.extend(f1.logs)

Room1.check_rules()
logs.extend(Room1.logs)

ff.check_rules()
logs.extend(ff.logs)

test1.check_rules()
logs.extend(test1.logs)