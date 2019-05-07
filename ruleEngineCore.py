from collections import defaultdict
import sys

class ListStream:
    def __init__(self):
        self.data = []
    def write(self, s):
        self.data.append(s)


class DynamicRuleEngine():
    def __init__(self):

        self.logs = []
        self.base1 ="""class BaseClass(object):\n\tdef __init__(self, classtype):\n\t\tself._type = classtype\n\ndef ClassFactory(name, argnames=[], BaseClass=BaseClass):\n\tdef __init__(self, **kwargs):\n\t\tsetattr(self, "logs", [])\n\t\tfor key, value in kwargs.items():\n\t\t\tif argnames:\n\t\t\t\tif key not in argnames:\n\t\t\t\t\traise TypeError("Argument %s not valid for %s" % (key, self.__class__.__name__))\n\t\t\tsetattr(self, key, value)\n\t\tBaseClass.__init__(self, name)\n\tdef check_rules(self):\n\t\tbase=self.logging+self.att_str+self.rule_str\n\t\tcodeobj = compile(base, 'fakemodule', 'exec')\n\t\tself.env = self.exec_env\n\t\texec(codeobj,self.env,self.env)\n\t\tself.logs.extend(self.env.get('inner_logs'))\n\tnewclass = type(name, (BaseClass,),{"__init__": __init__,"check_rules":check_rules})\n\treturn newclass"""
        
        self.base2 = """\nlogs=[]\ndef add_to_log(error):\n\tlogs.append(error)\n"""

        self.rules = """\n"""
        
    def ORMScriptClassGeneration(self, obj):
        return "{} = ClassFactory('{}')".format(obj.name,obj.name)


    def ORMScriptClassInstanceGeneration(self, obj):
        attributs = ""
        exec_env = "{}"
        if obj.parms:
            attributs += ", ".join(["{} = '{}'".format(i.param.name ,i.value) for i in obj.parms]) + ", "
        if obj.childs:

            chids_Arrays = {}
            for i in obj.object_type.childs:
                chids_Arrays[i.name+"s"]=[]

            # chids_Arrays = defaultdict(list)
            for i in obj.childs:
                chids_Arrays[i.object_type.name+"s"].append(i.name)

            attributs +=  ", ".join(["{} = {}".format(k,str("["+",".join(chids_Arrays[k])+"]")) for k in chids_Arrays]) + ", "
            attributs +=  ", ".join(["{} = {}".format(i.name ,i.name) for i in obj.childs]) + ", "

            exec_env = "{"+",".join(["'{}' : {}".format(i.name ,i.name) for i in obj.childs])+"}" #str({i.name:i.name for i in obj.childs})

        
        attributs += '{} = "{}"'.format("att_str",str(r"\n"+attributs.replace(", ",r"\n")+r"\n"))
        attributs += ",{} = '{}'".format("logging",r"""\ninner_logs=[]\ndef add_to_log(error):\n\tinner_logs.append(error)\n""")
        attributs += ',{} = {}'.format("exec_env",exec_env)

        # to do loop over rules and create_validation_rule
        rule_to_add = ""
        for i in obj.object_type.rules:
            syntax =i.syntax
            syntax = syntax.replace("\u2003",r"\t").replace("\t",r"\t")
            syntax = syntax.replace(r"&lt;" ,r"<").replace(r"&gt;" ,r">")
            syntax = syntax.replace(r"<br>",r"\n")
            syntax = syntax.replace(r"<p>",r"\n").replace(r"</p>","")
            syntax = syntax.replace(r"<div>",r"\n").replace(r"</div>","")
            syntax = r"{}".format(syntax)

            rule_to_add += self.create_validation_rule( i.id, r"{}".format(syntax))
        attributs += ',{} = "{}"'.format("rule_str",str(r"\n"+rule_to_add+r"\n"))

        return "{} = {}({})\n{}.check_rules()\nlogs.extend({}.logs)".format(obj.name,obj.object_type.name,attributs ,obj.name,obj.name)



    def classes_generation(self, objects):
        objects_str = ""
        for obj in objects:
            obj_str = self.ORMScriptClassGeneration(obj)
            objects_str = obj_str +"\n"+objects_str
        return objects_str


    def instances_generation(self, root_obj):
        instances_str = self.ORMScriptClassInstanceGeneration(root_obj)
        children = root_obj.childs
        if children:
            for child in children:
                inst_str = self.instances_generation(child)
                instances_str = inst_str +"\n"+instances_str
        return instances_str



    def add_to_log(self, error):
        self.logs.append(error)

    def add_validation_rule(self, rule_id, rule):
        if self.check_validation_rule(rule_id,rule) is True:
            self.rules += "try:\n\t" + rule.replace("\n","\n\t") + "\nexcept Exception as e:\n\tprint(e)\n\tadd_to_log('[exec][rule ({})]: '+str(e))".format(str(rule_id))
        # else:
            # raise Exception

    def create_validation_rule(self, rule_id, rule):
        return r"{}".format(r"\ntry:\n\t" + rule.replace(r"\n",r"\n\t") + r"\nexcept Exception as e:\n\tprint(e)\n\tadd_to_log('[exec][rule ({})]: '+str(e))\n".format(str(rule_id)) )


    def check_validation_rule(self, rule_id, rule):
        try:
            temp = compile(rule, 'fakerule', 'exec')
        except SyntaxError as e:
            self.add_to_log('[check_validation_rule][rule ({})]: '.format(rule_id)+str(e)+"\n"+'Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text))
            return False
        except Exception as e:
            self.add_to_log('[check_validation_rule][rule ({})]: '.format(rule_id)+str(e))
        except RuntimeError as e:
            self.add_to_log('[check_validation_rule][rule ({})]: '.format(rule_id)+str(e))
        return True

    def get_logs(self):
        sys.stdout = sys.__stdout__
        self.logs = list(set(self.logs))
        if "\n" in self.logs:
            self.logs.remove("\n")
        return self.logs
        

    
    def fit(self, objects, instances_root):
        sys.stdout = x = ListStream()

        
        self.base2+= self.classes_generation(objects)
        self.base2+= self.instances_generation(instances_root)
        # print(self.base2)

        self.logs.extend(x.data)
        sys.stdout = sys.__stdout__

        
        
    def run(self,log_level= 0):

        sys.stdout = x = ListStream()


        try:
            self.base = self.base1 + self.base2 + self.rules
            # self.base+="\nprint('finished with no errors yeaah !!')"
            # print(self.base)
            codeobj = compile(self.base, 'fakemodule', 'exec')
            env = {}
            exec(codeobj,{},env)
            self.logs.extend(env.get('logs'))

        except SyntaxError as e:
            self.add_to_log('[run][SyntaxError]: '+str(e)+"\n"+'Syntax error {} ({}-{}): {}'.format(e.filename, e.lineno, e.offset, e.text))

            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__
            print(self.base)

            return False
        except Exception as e:
            self.add_to_log('[run][Exception]: '+str(e))
            
            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__
            print(self.base)

            return False
        except RuntimeError as e:
            self.add_to_log('[run][RuntimeError]: '+str(e))
            
            self.logs.extend(x.data)
            sys.stdout = sys.__stdout__
            print(self.base)

            return False

        self.logs.extend(x.data)
        sys.stdout = sys.__stdout__

        return True

        
        