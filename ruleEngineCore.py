from collections import defaultdict
import sys
import re

class ListStream:
    def __init__(self):
        self.data = []
    def write(self, s):
        self.data.append(s)


class DynamicRuleEngine():
    def __init__(self):

        self.logs = []
        self.base1 ="""g={}\nclass BaseClass(object):\n\tdef __init__(self, classtype):\n\t\tself._type = classtype\n\ndef ClassFactory(name, argnames=[], BaseClass=BaseClass):\n\tdef __init__(self, **kwargs):\n\t\tsetattr(self, "logs", [])\n\t\tfor key, value in kwargs.items():\n\t\t\tif argnames:\n\t\t\t\tif key not in argnames:\n\t\t\t\t\traise TypeError("Argument %s not valid for %s" % (key, self.__class__.__name__))\n\t\t\tsetattr(self, key, value)\n\t\tBaseClass.__init__(self, name)\n\tdef check_rules(self):\n\t\ttry:\n\t\t\tbase=self.logging+self.att_str+self.rule_str\n\t\t\tcodeobj = compile(base, 'fakemodule', 'exec')\n\t\t\tself.env = self.exec_env\n\t\t\tglobal g\n\t\t\tself.env['parent']=self.parent\n\t\t\texec(codeobj,self.env,self.env)\n\t\t\tself.logs.extend(self.env.get('inner_logs'))\n\t\texcept SyntaxError as e:\n\t\t\tself.logs.append('[error][check_rules][SyntaxError]: '+str(e)+' Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text))\n\t\t\tself.logs.extend(x.data)\n\t\t\treturn False\n\t\texcept Exception as e:\n\t\t\tself.logs.append('[error][check_rules][Exception]: '+str(e))\n\t\t\tself.logs.extend(x.data)\n\t\t\treturn False\n\t\texcept RuntimeError as e:\n\t\t\tself.logs.append('[error][check_rules][RuntimeError]: '+str(e))\n\t\t\tself.logs.extend(x.data)\n\t\t\treturn False\n\tdef set_parent(self):\n\t\tglobal g\n\t\tself.parent=g.get(self.parent)\n\tnewclass = type(name, (BaseClass,),{"__init__": __init__,"check_rules":check_rules,"set_parent":set_parent})\n\treturn newclass"""
        
        self.base2 = """\nlogs=[]\ndef add_to_log(error):\n\tlogs.append(error)\n"""
        self.base3 = ""

        self.rules = """\n"""
        
    def ORMScriptClassGeneration(self, obj):
        return "{} = ClassFactory('{}')".format(obj.name,obj.name)


    def ORMScriptClassInstanceGeneration(self, obj):
        attributs = ""
        exec_env = "{}"
        childs_parents = ""

        if obj.parent:
            # childs_parents += r"'parent' : '{}'".format(obj.parent.name)
            childs_parents += r"parent = '{}'".format(obj.parent.name)

        if obj.object_type.parms:
            temp_parms = []
            temp_parms2= []
            if childs_parents:
                temp_parms2.append(childs_parents)
            else:
                temp_parms2.append("parent = ''")
            for i in obj.parms:
                temp_parms.append(i.param.name)
            for i in obj.object_type.parms:
                if i.name not in temp_parms:
                    temp_parms2.append("{} = {}".format(i.name ,"None"))

            # temp_parms = ["{} = '{}'".format(i.param.name ,i.value) for i in obj.parms]
            temp_parms = []
            for i in obj.parms:
                param_type = self.get_type(i.param.param_type)
                if param_type == str:
                    temp_parms.append("{} = '{}'".format(i.param.name ,param_type(i.value)))
                else:
                    temp_parms.append("{} = {}".format(i.param.name ,param_type(i.value)))

            # sys.stdout = sys.__stdout__
            # print("temp_parms : " , temp_parms ,"*"*100)

            temp_parms.extend(temp_parms2)
            attributs += "  ,  ".join(temp_parms)
            if attributs:
                attributs+= "  ,  "
        if obj.object_type.childs:

            chids_Arrays = {}
            for i in obj.object_type.childs:
                chids_Arrays[i.name+"s"]=[]

            # chids_Arrays = defaultdict(list)
            for i in obj.childs:
                chids_Arrays[i.object_type.name+"s"].append(i.name)

            tmp1 =  "  ,  ".join(["{} = {}".format(k,str("["+",".join(chids_Arrays[k])+"]")) for k in chids_Arrays])
            if tmp1:
                attributs+= tmp1 +"  ,  "
            tmp1 =  "  ,  ".join(["{} = {}".format(i.name ,i.name) for i in obj.childs])
            if tmp1:
                attributs+= tmp1 +"  ,  "

            temp2 = ["'{}' : {}".format(i.name ,i.name) for i in obj.childs]
            # if childs_parents:
                # temp2.append(childs_parents)
            exec_env = "{"+",".join(temp2)+"}" #str({i.name:i.name for i in obj.childs})
        
        line = re.sub(r"\\nparent = '.*'\\n", r"\n", attributs.replace("  ,  ",r"\n"))

        attributs += '{} = "{}"'.format("att_str",str(r"\n"+line+r"\n"))
        attributs += ",{} = '{}'".format("logging",r"""\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n""")
        attributs += ',{} = {}'.format("exec_env",exec_env)

        # to do loop over rules and create_validation_rule
        rule_to_add = """"""
        for i in obj.object_type.rules:
            syntax =i.syntax
            syntax = syntax.replace("\u2003",r"\t").replace("\t",r"\t")
            syntax = syntax.replace(r"&lt;" ,r"<").replace(r"&gt;" ,r">")
            syntax = syntax.replace(r"<br>",r"\n")
            syntax = syntax.replace(r"<p>",r"\n").replace(r"</p>","")
            syntax = syntax.replace(r"<div>",r"\n").replace(r"</div>","")
            syntax = syntax.replace(r'"',r"'")
            syntax = r"{}".format(syntax)

            rule_to_add += self.create_validation_rule( i.name, r"{}".format(syntax))
        attributs += ',{} = "{}"'.format("rule_str",str(r"\n"+rule_to_add+r"\n"))


        return "{} = {}({})\ng['{}']={}".format(obj.name,obj.object_type.name,attributs,obj.name,obj.name) ,"\n{}.set_parent()".format(obj.name) ,"\n{}.check_rules()\nlogs.extend({}.logs)".format(obj.name,obj.name,obj.name)

    def get_type(self, type_id):
        def proccess_boolean(x):
            if type(x) is str:
                x= x.strip().lower()
                if x == "true":
                    return True
                else:
                    return False
            else:
                return bool(x)

        def proccess_list(x):
            # sys.stdout = sys.__stdout__
            # print("x : " , x ,"*"*100)
            return list(eval(x))

        def proccess_dict(x):
            return dict(eval(x))

        self.types = {"string":str,"integer":int,"boolean":proccess_boolean,"float":float,"list":proccess_list,"dict":proccess_dict}

        # types = [{"id":1,"text":"string"},{"id":2,"text":"integer"},{"id":3,"text":"boolean"},{"id":4,"text":"float"},{"id":5,"text":"list"},{"id":6,"text":"dict"}]
        # sys.stdout = sys.__stdout__

        # print("type_id : " , type_id ,"*"*100)

        return self.types.get(str(type_id))


    def classes_generation(self, objects):
        objects_str = ""
        for obj in objects:
            obj_str = self.ORMScriptClassGeneration(obj)
            objects_str = obj_str +"\n"+objects_str
        return objects_str


    def instances_generation(self, root_obj):
        instances_str,set_parent_str ,check_rules_str = self.ORMScriptClassInstanceGeneration(root_obj)
        children = root_obj.childs
        if children:
            for child in children:
                inst_str,parent_str ,check_str = self.instances_generation(child)
                instances_str = inst_str +"\n"+instances_str
                check_rules_str = check_str +"\n"+ check_rules_str
                set_parent_str = parent_str +"\n"+ set_parent_str
        return instances_str,set_parent_str ,check_rules_str



    def add_to_log(self, error):
        self.logs.append(error)

    def add_validation_rule(self, rule_id, rule):
        if self.check_validation_rule(rule_id,rule) is True:
            self.rules += "try:\n\t" + rule.replace("\n","\n\t") + "\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule ({})]: '+str(e))".format(str(rule_id))
        # else:
            # raise Exception

    def create_validation_rule(self, rule_id, rule):
        return r"{}".format(r"\ntry:\n\t" + rule.replace(r"\n",r"\n\t") + r"\nexcept Exception as e:\n\tadd_to_log('[error][exec][rule ({})]: '+str(e))\n".format(str(rule_id)) )


    def check_validation_rule(self, rule_id, rule):
        try:
            temp = compile(rule, 'fakerule', 'exec')
            # exec(temp)
        except SyntaxError as e:
            self.add_to_log('[error][check_validation_rule][rule ({})]: '.format(rule_id)+str(e)+"\n"+'Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text))
            return False
        except Exception as e:
            self.add_to_log('[error][check_validation_rule][rule ({})]: '.format(rule_id)+str(e))
        except RuntimeError as e:
            self.add_to_log('[error][check_validation_rule][rule ({})]: '.format(rule_id)+str(e))
        return True

    def get_logs(self):
        sys.stdout = sys.__stdout__
        # self.logs = list(set(self.logs))
        while "\n" in self.logs:
            self.logs.remove("\n")
        # self.logs.reverse()
        return self.logs
        

    
    def fit(self, objects, instances_root):
        sys.stdout = x = ListStream()


        try:



        
            self.base2+= self.classes_generation(objects)
            temp_base2 ,temp_base4,temp_base3 = self.instances_generation(instances_root)
            self.base2 += temp_base2
            self.base3 += temp_base4
            self.base3 += temp_base3
            # print(self.base2)


        except SyntaxError as e:
            self.add_to_log('[error][run][SyntaxError]: '+str(e)+"\n"+'Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text))

            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__

            return False

        except RuntimeError as e:
            if "name 'x' is not defined" in  str(e):
                self.add_to_log('[error][run][Exception]: '+" trying to use undefined parameter check rules parms names")
            else:
                self.add_to_log('[error][run][RuntimeError]: '+str(e))
            
            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__

            return False

        except Exception as e:
            if "name 'x' is not defined" in  str(e):
                self.add_to_log('[error][run][Exception]: '+" trying to use undefined parameter check rules parms names")
            else:
                self.add_to_log('[error][run][Exception]: '+str(e))


            
            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__

            return False
        

        self.logs.extend(x.data)
        sys.stdout = sys.__stdout__

        return True

        
        
    def run(self,log_level= 0):

        sys.stdout = x = ListStream()


        try:
            self.base = self.base1 + self.base2+ self.base3 + self.rules
            # self.base+="\nprint('finished with no errors yeaah !!')"
            # print(self.base)
            codeobj = compile(self.base, 'fakemodule', 'exec')
            env = {}
            exec(codeobj,{},env)
            self.logs.extend(env.get('logs'))

        except SyntaxError as e:
            self.add_to_log('[error][run][SyntaxError]: '+str(e)+"\n"+'Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text))

            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__
            print(self.base)

            return False

        except RuntimeError as e:
            if "name 'x' is not defined" in  str(e):
                self.add_to_log('[error][run][Exception]: '+" trying to use undefined parameter check rules parms names")
            else:
                self.add_to_log('[error][run][RuntimeError]: '+str(e))
            
            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__
            print(self.base)

            return False

        except Exception as e:
            if "name 'x' is not defined" in  str(e):
                self.add_to_log('[error][run][Exception]: '+" trying to use undefined parameter check rules parms names")
            else:
                self.add_to_log('[error][run][Exception]: '+str(e))


            
            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__
            print(self.base)

            return False
        

        self.logs.extend(x.data)
        sys.stdout = sys.__stdout__
        print(self.base)
        return True

        
        