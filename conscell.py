# -'- coding: utf-8 -'-
import sys
import re
import copy
import traceback


empty = 0     # 00000
lst  =  1     # 00001
atom =  2     # 00010

atm_int = 6   # 00110
atm_str = 10  # 01010
atm_sym = 18  # 10010
atm_symb= 19  # 10011

boolspec = 3  # 00011

specs = { empty:'EMPTY' ,
          lst:'LIST' ,
          atom:'ATOM' ,
          atm_int:'INT' ,
          atm_str:'STR' ,
          atm_sym:'SYMBOL' ,
          atm_symb:'FUNC BODY' ,
          boolspec:'BOOL' }

gsymtab = {}  # symbol table
gtab = gsymtab

traceflg = True

def prt(a,b):
    if traceflg == True:
        print('{0}: {1}'.format(a,b))
    else:
        pass

def msg(a,b):
    print('{0}: {1}'.format(a,b))
    
    
def ontab(key,tab):
    prt('@ontab','chk')
    if lookup(key, tab) or lookup(key, gtab):
        return True
    else:
        return False
        
        
def look(key,tab):
    if lookup(key,tab) :
        ret = tab[key]
        prt('@look from tab','{0}:{1}'.format(key, ret.toStrV()))
    else:
        ret = gtab[key]
        prt('@look from gtab','{0}:{1}'.format(key, ret.toStrV()))
    
    return ret


def lookup(key, tab):
    
    if (key in tab):
        ret = True
    else:
        ret = False
        
    prt('@lookup','{0}:{1}'.format(key, ret))
    return ret


def diccopy(tab):
    newdic = {}
    newdic.update(tab)
    return newdic
    

            
class sexp:
    def __init__(self,spec,val,symtab):
        self.spec = spec   # lst or atom
        self.val = val
        self.tab = symtab
    
    def getspec(self):
        return self.spec
    
    def eval(self, tab):
        self.tab = tab
        prt('@SEXP EVAL START',self.toStr())
        #ret = self.evalSYM(tab)
        #prt('@SEXP EVALSYM=>',ret.toStrV())
        ret = self.evalbody(tab)
        #ret2 = ret.evalbody(tab)
        prt('@SEXP EVAL END',self.toStr())
        #prt('@SEXP EVAL END=>',ret2.toStrV())
        return ret
        #return ret2
        
        
    def evalSYMatm(self, tab):
        self.tab = tab
        prt('@evalSYMatm spec',specs[self.getspec()])
        
        if self.getspec() == atm_sym :
        	prt('@evalSYMatm sexp=sym', self.toStrV())
        	
        	if ontab(self.val, tab):
        		rep = look(self.val, tab)
        		
        		if rep.getspec() not in [ atm_int , atm_str , atm_symb, boolspec ]:
        			# list or sym
        			r = rep.evalSYM(tab)
        		else:
        			r = rep
        			
        		prt('@evalSYMatm sexp=>', r.toStrV())
        		return r
        		
        	else:
        		msg('@evalSYM sexp: unknown symbol',self.val)
        		
        		#raise Exception
        		
        return self
        
        				
    def evalSYM(self, tab):
        if self.getspec() != lst:
        	prt('@evalSYM','not List')
        	prt('@evalSYM notList',self.toStrV())
        	return self.evalSYMatm(tab)
        	
        else: # spec == lst 
        	prt('@evalSYM','List')
        	carv = self.carval
        	cdrv = self.cdrval
        	prt('@evalSYM lst carv.spec', specs[carv.getspec()])
        	prt('@evalSYM lst carv', carv.toStr())
        	prt('@evalSYM lst cdrv.spec', specs[cdrv.getspec()])
        	prt('@evalSYM lst cdrv', cdrv.toStr())
        	
        	if carv.getspec() == atm_sym :
        		prt('@evalSYM lst carv=sym START evalSYMatm', carv.toStrV())
        		carrep = carv.evalSYMatm(tab)
        		prt('@evalSYM lst carv=sym END evalSYMatm=>', carrep.toStrV())	
        		
        	elif carv.getspec() in [ atm_int, atm_str, atm_symb, boolspec]:
        		prt('@evalSYM lst carv=intstrsymbbool', carv.toStrV())
        		carrep = carv
        	
        	else: # carv == lst
        		prt('@evalSYM lst carv=lst START eval car', carv.toStrV())
        		carrep = carv.evalSYM(tab)
        		prt('@evalSYM lst carv=lst END eval car=>', carrep.toStrV())
        			
        
        
        	if carrep.val == 'quote' and carrep.getspec() == atm_symb:
        		prt('@evalSYM lst carv=quote', carv.toStrV())
        		cdrrep = cdrv
        		prt('@evalSYM lst carv=quote cdrv=', cdrrep.toStrV())
        	else:
        		prt('@evalSYM lst START eval cdr',cdrv.toStrV())
        		prt('@evalSYM lst cdrspec',specs[cdrv.getspec()])
        		cdrrep = cdrv.evalSYM(tab)
        		print(cdrrep)
        		prt('@evalSYM lst END eval cdr=>', cdrrep.toStrV())
        	
        	prt('@evalSYM lst car=sym cdr=>', cdrrep.toStrV())
        
        	r = conscell(carrep, cdrrep, tab)
        
        	prt('@evalSYM lst=>', r.toStrV())
        
        	return r
        
        
    def evalsexp(self, body, tab):
        self.tab = tab
        if body.getspec() == atm_sym :
            prt('@evalsexp body.spec', specs[body.getspec()])
            if ontab(body.val, self.tab):
                #(body.val in self.tab):
                prt('@evalsexp body.val(SYMBOL)', 'is IN TAB' )
                prt('@evalsexp SYMBOL', body.val)
                prt('@evalsexp SYMBOLs value', look(body.val, self.tab).toStr())
                return look(body.val, self.tab)
            else:
                # not in symbol table
                msg('@evalsexp: ERR unknown symbol', body.val)
                raise Exception
        else:
            # int str
            prt('@evalsexp body.spec', specs[body.getspec()])
            prt('@evalsexp value', body.val)
            return body
    
    
    def evalsymb(self, body, tab):
        self.tab = tab
        prt('@evalsymb START car=body', body.toStrV())
        cdrv = self.cdrval
        prt('@evalsymb cdr', cdrv.toStrV())
        #body.tab = self.tab
        ret = body.eval(cdrv, self.tab)
        prt('@evalsymb ret=body(cdrv)', ret)
        prt('@evalsymb ret.spec', specs[ret.getspec()])
        prt('@evalsymb END car=body', body.toStrV())
        
        return ret
    
    
    def evallist(self, carv, cdrv, tab):
        self.tab = tab
        prt('@evallist car.spec', specs[carv.getspec()])
        prt('@evallist car', carv.toStrV())
        prt('@evallist car','START car.eval')
        
        op = carv.eval(self.tab)
        prt('@evallist car.eval(=op).toStrV', op.toStrV())
        prt('@evallist car.eval(=op).toStr', op.toStr())
        if op.getspec() == atm_symb:
            prt('@evallist op(symb):START op.eval(cdr)', cdrv.toStrV())
            r = op.eval(cdrv, self.tab)
            prt('@evallist op(symb):END op.eval(cdr)', r.toStrV())
        else:
            prt('@evallist :START (cons op . cdr)', cdrv.toStrV())
            if cdrv == nil:
                #r = op.eval()
                r = conscell(op.eval(self.tab), cdrv.eval(self.tab), self.tab)
                #r = self
                prt('@evallist (cons op . cdr)=op', op.toStr())
            else:
                r = conscell(op.eval(self.tab), cdrv.evalSYM(self.tab), self.tab)
                prt('@evallist (cons op . cdr)', r.toStrV())
            prt('@evallist :END (cons op . cdr)',r.toStrV())
            
        return r
    
    
    def evalbody(self, tab):
        self.tab = tab
        if self.getspec() != lst:
            return self.evalsexp(self, self.tab)
                
        else: # spec == lst
            carv = self.carval
            cdrv = self.cdrval
            prt('@eval lst carv.spec', specs[carv.getspec()])
            prt('@eval lst carv', carv.toStr())
            prt('@eval lst cdrv.spec', specs[cdrv.getspec()])
            prt('@eval lst cdrv', cdrv.toStr())
            # list's car=sym
            if carv.getspec() == atm_sym :
                prt('@eval lst carv=sym', carv.toStrV())
                body = \
                look(carv.val, self.tab)
                
                if body.getspec() == atm_symb : # car=sym=symb
                    prt('@eval lst car=sym','atm_symb')
                    return \
                    self.evalsymb(body, self.tab)
                    
                else: # car=sym=sexp
                    # body is variables
                    prt('@eval lst car=sym','not atm_symb then as sexp')
                    return \
                    self.evalsexp(body.eval(self.tab), self.tab)
                    '''
                    msg('@eval lst: ERR unknow symbols function',carv.val)
                    raise Exception
                    '''
        
            elif carv.getspec() == atm_symb :
                # list's car=symb
                return \
                self.evalsymb(carv, self.tab)
            
            else: # list's car=list
                #input('@eval lst:START EVALLIST: push ret')
                return \
                self.evallist(carv, cdrv, self.tab)
            
            
    def toStr(self):
        if self.spec == lst :
            #prt('@toStr','CONS')
            return self.toStrCC()
        else:
            #prt('@toStr','SEXP')
            return self.toStrSEXP()
                
            
    def toStrSEXP(self):
        if self.spec == atm_int :
            #prt('@toStrS int',self.val)
            s = str(self.val)
        elif self.spec == atm_str :
            #prt('@toStrS str',self.val)
            s = "'" + self.val + "'"
        elif self.spec == boolspec :
            #prt('@toStrS bool',self.val)
            if self.val == False:
                s = 'nil'
            else:
                s = 't'
        else: #symbol?
            #prt('@toStrS symbol?',self.val)
            s = self.val # symbol name
            #dict(self.val).show()
        #prt('@toStrS s',s)
        return s
        
    def toStrCC(self):
        # list
        #  a d
        #    +-a d
        #        +-a d
        #
        # conscell
        #  a d
        #  | +- without nil
        #  |
        #  +- without empty
        #
        carv = self.val.car()
        cdrv = self.val.cdr()
        #prt('@toStrC carv',carv)
        #prt('@toStrC cdrv',cdrv)
        
        if carv.getspec() == lst:
            #prt('@toStrC car=lst','START')
            s  = '('
            s += carv.toStr()
            s += ')'
            #prt('@toStrC car=lst','END')
        else:
            #prt('@toStrC car!=lst','START')
            s = carv.toStr()
            #prt('@toStrC car!=lst:car',s)
            #prt('@toStrC car!=lst','END')
        
        if cdrv == nil:  # list edge
            return s
            
        elif cdrv.getspec() in [atm_int, atm_str, atm_sym] :
                s += ' . '
                s += cdrv.toStr()
        else:
                s += ' ' 
                s += cdrv.toStr()
                
        return s


    def toStrV(self):
        spec = self.getspec()
        if spec == lst:
            s = '(CONS '
            carv = self.car()
            s += carv.toStrV()
            s += ' . '
            cdrv = self.cdr()
            #print('dbg',cdrv)
            s += cdrv.toStrV()
            s += ')'
            return s
        elif spec == atm_int :
            s = str(self.val)
            return s
        elif spec == atm_str :
            s = "'" + self.val + "'"
            return s
        elif spec == boolspec :
            if self.val == False:
                s = 'nil'
                return s
            else:
                s = 't'
                return s
        else: #symbol?
            s = self.val # symbol name
            return s
            


nil = sexp(boolspec,False,gsymtab)
t = sexp(boolspec,True,gsymtab)


class conscell(sexp):
    def __init__(self,v1,v2,tab):
        super().__init__(lst,self,tab)
        self.setcar(v1)
        self.setcdr(v2)
    
    '''
    def eval(self, tab):
        self.tab = tab
        prt('@CONS EVAL START',self.toStr())
        ret = self.evalbody(self.tab)
        prt('@CONS EVAL END',self.toStr())
        return ret
    '''
    
    
    def setcar(self,v):
        self.carval = v
        #self.carspec = v.getspec()
    
    def setcdr(self,v):
        self.cdrval = v
        #self.cdrspec = v.getspec()
    
    def car(self):
        return self.carval
        
    def cdr(self):
        return self.cdrval
        

class sym(sexp):
    def __init__(self,val,body,tab):
        super().__init__(atm_symb, self, tab)
        self.val  = val
        self.body = body

    def eval(self,obj, tab):
        self.tab = tab
        return self.body(obj, self.tab)
    
    
class env:
    def __init__(self, tab):
        self.length = 0
        
        self.errno = 0
        self.errin = ''
        self.errmsg = [
            'no error' ,
            'syntax error', 
            'arithmetic error',
            'unbound variable',
            'unknown',
        ]
        
        self.ESYNTAX = 1
        self.EARITHM = 2
        self.EUNBIND = 3
        self.EUNKNWN = 4


        if len(gtab) == 0:
            self.builtins()
        
        self.tab = {}
        self.tab.update(tab)
        

    def err(self,no,where):
        s = self.errmsg[no]
        s += '@'
        s += where
        print(s)




    def add(self,tab,name,body):
        tab[name] = body
        return tab
        
    
    def delname(self,tab,name) :
        if lookup(tab,name) :
            del tab[name]
        else:
            self.err(self.EUNBIND, 'delname')           
        return tab
    
    
    def update(self,tab, name, body):
        prt('@update key:val','{0}:{1}'.format(name, body.val))
        if lookup(name, tab) : 
            if tab[name].getspec() in [ atm_int , atm_str ]: 
           
                tab[name].val = body.val
            else:
                self.add(tab, name, body)
        else:
            self.add(tab, name, body)
                
        return tab
            
            
    def eval(self,obj,tab):
        return obj.eval(tab)
        
    
    def op_ltab(self,obj,tab):
        fc = obj.car().eval(tab)
        cdrv = obj.cdr()
        tablst = list(fc.tab.items())
        for x in fc.tab.keys():
            str = x + ':' + fc.tab[x].toStr()
            print(str)
        
        c = self.tabsub(tablst,fc.tab)
        if cdrv == nil :
            return conscell(c, nil, tab)
        else:
            return conscell(c, self.op_ltab(cdrv, tab), tab)
    
    def op_tab(self,tab):
        
        alltab = {}
        alltab.update(gtab)
        alltab.update(tab)
        
        diclist = \
        list(alltab.items())
        for x in tab.keys():
            str = x + ':' + alltab[x].toStr()
            print(str)
        return self.tabsub(diclist, tab)
    
    
    def tabsub(self, tablst, tab):
        c = tablst.pop(0)
        ca = sexp(atm_str, c[0] , tab)  # key
        cs = conscell(ca, conscell(look(c[0], tab), nil, tab), tab)
        if len(tablst) == 0:
            return conscell(cs, nil, tab)
        else:
            return conscell(cs, self.tabsub(tablst, tab), tab)
    
    
    def op_load(self,obj,tab):
    	fx = obj.car().eval(tab).val
    	prt('@load fx',fx)
    	fn = fx.replace('"','')
    	prt('@load fn',fn)
    	if True: #try:
    		with open(fn,'rt') as f:
    			line = f.readline()
    			while line :
    				o = lisp.token(line)
    				prt('token:',o.toStrV())
    				try:
    					e = lisp.eval(o)
    				except:
    					e = traceback.print_exc()
    
    				try:
    					p = lisp.printer(e)
    				except:
    					print(traceback.print_exc())
    					
    				line = f.readline()
    				
    	else: #except:
    
    		raise Exception
    		print(traceback.print_exc())
    		return nil
    			
    	return e
    		
    
    
    def op_cons(self,carv,cdrv,tab):
        newcons = conscell(carv.eval(tab), cdrv.eval(tab), tab)
        #newcons.setcar(carv)
        #newcons.setcdr(cdrv)
        return newcons
     
    def cons_op(self,obj,tab):
        # (cons (cons val1 (cons val2 nil)))
        carv = obj.car()
        cdrv = obj.cdr()
        return self.op_cons(carv, cdrv, tab)
     
     
    def op_car(self,obj,tab):
        cons = obj.car()
        prt('@op_car cons', cons.toStrV())
        carv = cons.eval(tab).car()
        return carv


    def op_cdr(self,obj,tab):
        cons = obj.car()
        cdrv = cons.eval(tab).cdr()
        return cdrv
    
    
    def op_atom(self,obj,tab):
        objv = obj.car().eval(tab)
        vs = objv.getspec()
        atomp = vs & atom
        if atomp == atom :
            return t
        else:
            return nil
            
    
    def op_eq(self,obj,tab):
        # (eq (a (b (c . nil))))
        carv = obj.car().eval(tab).val
        cdrv = obj.cdr()
        if cdrv == nil :
            return t
        eqv = self.eqsub(cdrv,tab)
        prt('@eq_op carv cdrv', '{0},{1}'.format(carv , eqv))
        if carv == eqv :
            return t
        else:
            return nil
            
    def eqsub(self,obj,tab):
        carv = obj.car().eval(tab).val
        cdrv = obj.cdr()
        if cdrv == nil :
            return carv
        else:
            eqv = self.eqsub(cdrv,tab)
            prt('@eqsub eqv',eqv)
            if carv == eqv:
                return carv
            else:
                return eqv
    
    
    def op_cond(self,obj,tab):
    	op = obj.car()
    	cdrv = obj.cdr()
    	prt('@op_cond op', op.toStrV())
    	prt('@op_cond cdrv', cdrv.toStrV())
    	chk = self.cond_op(op, tab)
    	prt('@op_cond chl', chk.toStrV())
    	if chk != nil :
    		return chk
    	else:
    		return self.op_cond(cdrv, tab)
    
    def cond_op(self,op, tab):
    	cond = op.car().eval(tab).val
    	cdrv = op.cdr().car().cdr()
    	prt('@cond_op cond',cond)
    	prt('@cond_op cdrv',cdrv.toStrV())
    	if cond == False :
    		return nil
    	else:
    		return cdrv.eval(tab)
    		
    
    def op_if(self,obj,tab):
        cond = obj.car().eval(tab).val
        cdrt = obj.cdr().car()
        cdrn = obj.cdr().cdr().car()
        if cond == False :
            return cdrn.eval(tab)
        else:
            return cdrt.eval(tab)
    
    
    def op_lambda(self,obj,tab):
        prt('@op_lambda obj', obj.toStr())
        lamO = lambdaBody(tab, obj)
        return lamO


    def op_gt(self,obj,tab):
        carv = obj.car().eval(tab).val
        cdrv = obj.cdr()
        if cdrv == nil :
            return t
        gtv = self.glsub(cdrv,0,tab)
        prt('@op_gt carv cdrv', '{0},{1}'.format(carv , gtv))
        if carv > gtv :
            return t
        else:
            return nil
            
            
    def op_lt(self,obj,tab):
        carv = obj.car().eval(tab).val
        cdrv = obj.cdr()
        if cdrv == nil :
            return t
        gtv = self.glsub(cdrv,1,tab)
        prt('@op_lt carv cdrv', '{0},{1}'.format(carv , gtv))
        if carv < gtv :
            return t
        else:
            return nil
            
            
    def glsub(self,obj,d,tab): #d 0 >,1 <
        carv = obj.car().eval(tab).val
        cdrv = obj.cdr()
        if cdrv == nil :
            return carv
        else:
            gtv = self.glsub(cdrv,d, tab)
            prt('@glsub gtv',gtv)
            if d == 0:
                if carv > gtv:
                    return carv
                else:
                    return gtv
            else: # d == 1
                if carv < gtv:
                    return carv
                else:
                    return gtv
                    
    
    def op_add(self,obj,tab):
        carv = obj.car()
        cdrv = obj.cdr()
        if cdrv == nil : # list edge
            return sexp(atm_int, carv.eval(tab).val, tab)
        else:
            # add(o) ->
            #       o.car + add(o.cdr))
            return sexp(atm_int , carv.eval(tab).val + self.op_add(cdrv,tab).val, tab)
    
    
    def op_dec(self,obj,tab):
        carv = obj.car()
        cdrv = obj.cdr()
        if cdrv == nil : # list edge
            return sexp(atm_int, carv.eval(tab).val, tab)
        else:
            # dec(o) ->
            #       o.car - add(o.cdr))
            return sexp(atm_int , carv.eval(tab).val - self.op_add(cdrv,tab).val, tab)
    
    def op_mul(self,obj,tab):
        carv = obj.car()
        cdrv = obj.cdr()
        if cdrv == nil : # list edge
            return sexp(atm_int, carv.eval(tab).val, tab)
        else:
            # mul(o) ->
            #       o.car * mul(o.cdr))
            prt('@mul obj.car',carv.toStrV())
            v1p = carv.eval(tab)
            prt('@mul v1',v1p.toStrV())
            v1 = v1p.val
            v2 = self.op_mul(cdrv, tab).val
            prt('mul v1,v2','{0},{1}'.format(v1,v2))
            return sexp(atm_int , v1 * v2, tab)

    def op_div(self,obj,tab):
        carv = obj.car()
        cdrv = obj.cdr()
        if cdrv == nil : # list edge
            return sexp(atm_int, carv.eval(tab).val, tab)
        else:
            # div(o) ->
            #       o.car / mul(o.cdr))
            return sexp(atm_int , carv.eval(tab).val / self.op_mul(cdrv, tab).val, tab)
    
    
    def op_quote(self,obj,tab):
        prt('@op_quote obj', obj.toStrV())
        v = obj.car()
        prt('@op_quote obj.car',v.toStrV())
        return v


    def op_let(self,key,body,tab):
        self.update(tab, key, body)

    def let_op(self,obj,tab):
        name = obj.car().val
        prt('@op_let car', obj.car().toStrV())
        prt('@op_let cdr', obj.cdr().toStrV())
        #body = self.eval( obj.cdr())
        body = obj.cdr().car().eval(tab)
        #body = obj.cdr()
        prt('@op_let cdr.car().eval()=body', body.toStr())
        prt('@op_let bodyspec:', specs[body.spec])
        prt('@op_let body(raw)', body)
        self.op_let(name,body,tab)
        return body
        #return sexp(atm_sym, name, tab)

    def op_define(self,name,body):        
        self.update(gtab, name, body)
    
    
    def define_op(self,obj,tab):
        name = obj.car().val
        prt('@op_def car', obj.car().toStrV())
        prt('@op_def cdr', obj.cdr().toStrV())
        #body = self.eval(obj.cdr())
        body = obj.cdr().car().eval(tab)
        #body = obj.cdr()
        prt('@op_def cdr.car().eval()=body', body.toStr())
        prt('@op_def bodyspec:', specs[body.spec])
        prt('@op_def body(raw)', body)
        self.op_define(name,body)
        return body
        #return sexp(atm_sym, name, tab)
        
    
    def builtins(self):
        self.add(gtab, 'cons', sym('cons' , lambda x, tab: self.cons_op(x,tab), gtab))
        self.add(gtab, 'car', sym('car', lambda x, tab: self.op_car(x,tab), gtab))
        self.add(gtab, 'cdr', sym('cdr', lambda x, tab: self.op_cdr(x,tab), gtab))
        self.add(gtab, 'atom' , sym('atom', lambda x, tab: self.op_atom(x,tab), gtab))
        self.add(gtab, 'lambda', sym('lambda', lambda x, tab: self.op_lambda(x,tab), gtab))
        self.add(gtab, 'eq', sym('eq', lambda x, tab:self.op_eq(x,tab), gtab))
        self.add(gtab, '>', sym('>', lambda x, tab:self.op_gt(x,tab), gtab))
        self.add(gtab, '<', sym('<', lambda x, tab:self.op_lt(x,tab), gtab))
        self.add(gtab, 'define',sym('define', lambda x, tab: self.define_op(x,tab), gtab))
        self.add(gtab, 'set!',sym('set!', lambda x, tab: self.let_op(x,tab), gtab))
        self.add(gtab, 'quote',sym('quote', lambda x, tab: self.op_quote(x,tab), gtab))
        self.add(gtab, '+', sym('+', lambda x, tab: self.op_add(x,tab), gtab))
        self.add(gtab, '-', sym('-', lambda x, tab: self.op_dec(x,tab), gtab))
        self.add(gtab, '*', sym('*', lambda x, tab: self.op_mul(x,tab), gtab))
        self.add(gtab, '/', sym('/', lambda x, tab: self.op_div(x,tab), gtab))
        self.add(gtab, 'nil' , sym('nil', lambda x, tab: nil, gtab))
        self.add(gtab, 't' , sym('t', lambda x, tab: t, gtab))
        self.add(gtab, 'showtab', sym('showtab', lambda x, tab: self.op_tab(tab), gtab))
        self.add(gtab, 'if', sym('if', lambda x, tab: self.op_if(x,tab), gtab))
        self.add(gtab, 'cond', sym('cond', lambda x, tab: self.op_cond(x,tab), gtab))
        self.add(gtab, 'eval', sym('eval', lambda x, tab: self.eval(x,tab), gtab))
        self.add(gtab, 'showlocal', sym('showlocal', lambda x, tab: self.op_ltab(x, tab), gtab))
        self.add(gtab, 'load', sym('load', lambda x, tab: self.op_load(x, tab), gtab))
        



class tokenizer:
    def __init__(self,txt,deli):
        self.txt = txt
        self.dl = list(deli)  # delimiters without spaces
        self.it = iter(list(txt.strip()))
        self.lst = []
        
    def tokenlist(self):
        str = ''
        c = self.nextc()
        while c != False:
            #print('c:',c)
            if  c ==' ' or c == '\t' or c == '\n' :
                self.addc(str)
                str = ''
            elif c in self.dl:
                self.addc(str)
                str = ''
                self.addc(c)
            else:
                str = str + c
            
            c = self.nextc()
            #print('str:',str)
            
        self.addc(str)
        return self.lst
    
    def addc(self,s):
        if s != '' :
            self.lst.append(s)
            
    def nextc(self):
        try:
                c = next(self.it)
        except:
                c = False
        return c



class sexpobj:
    def __init__(self, lobj, tab):
        self.tab = tab
        self.lobj = lobj
        
    def expr(self):
        s = self.lobj.pop(0)
        if s == '(' : # list
            ret = self.mkcons(self.lobj, self.tab)
        else: # sexp
            ret = self.mksexp(s, self.tab)
        return ret
    
    def mkcons(self, lobj, tab):
        s = lobj.pop(0)
        prt('@mkcons s',s)
        if s == '(' : # inner cons
            car = self.mkcons(lobj, tab)
        elif s == ')' : # inner nil
            car = nil 
        else:
            car = self.mksexp(s, tab)
        
        nexts = lobj[0]
        prt('@mkcons:nexts',nexts)
        if nexts == ')' :
            cdr = nil
            lobj.pop(0)
        else:
            cdr = self.mkcons(lobj, tab)
        ret = conscell(car, cdr, tab)
        return ret
        
        
    def mksexp(self, s, tab):
        v = s
        prt('@MKSEXP:v',v)

        if v == 'nil':
            prt('@mksexp','nil')
            return nil
        else:
            try:
                vi = v.isdigit()
            except:
                vi = False
            if vi != False :
                prt('@mksexp','int')
                r = sexp(atm_int, int(v), tab)
            elif re.match('"',v) :
                prt('@mksexp','str')
                r = sexp(atm_str, v, tab)
            else:
                prt('@mksexp','sym')
                r = sexp(atm_sym, v, tab)
            return r

class repl:
    def __init__(self,tab):
        self.tab = tab
        self.l = env(self.tab)
        self.delimiter = '()'
        self.prompt = 'lisp> '
        
        
    def readtxt(self):
        txt = ''
        while txt == '' :
            txt = str(input(self.prompt))
        return txt
        
    
    def token(self,txt):
        if txt[0] == '!':
        	return nil
        
        tk = tokenizer(txt, self.delimiter)
        inputlist = tk.tokenlist()
        tkobj = sexpobj(inputlist, self.tab)
        inputobj = tkobj.expr()
        prt('@token obj', inputobj.toStrV())
        return inputobj
    
    def eval(self,obj):
        if obj == nil:
        	return nil
        ev = self.l.eval(obj,self.tab)
        return ev
    
    def printer(self,obj):
        p = obj.toStr()
        #p = obj.toStrV()
        print('eval:',p)
        return obj


class lambdaBody(sym):
    def __init__(self, tab, obj):
        prt('@lamb obj', obj.toStr())
        self.objs = obj
        prt('@lamb obj.car', obj.car().toStr())
        self.args = obj.car()
        prt('@lamb obj.cdr', obj.cdr().toStr())
        self.body = obj.cdr().car()
        
        prt('@lamb args:', self.args.toStr())
        prt('@lamb body:', self.body.toStr())
        #self.arglist = self.listArgs(self.args)
        
        self.tab = diccopy(tab)
        #self.tab = {}
        self.env = env(self.tab) #local scope
        self.spec = atm_symb
        self.val = obj.toStr()
        prt('@lamb lambda val',self.val)
        
    
    def toStr(self):
        return self.val
        
        
    def listArgs(self,obj):
        #
        # return args symbols list
        #
        lst = []
        prt('lstarg obj.car',obj.car().val)
        lst.append(obj.car().val)
        prt('lstarg lst',lst)
        if obj.cdr() == nil:
            return lst
        else:
            rlst = self.listArgs(obj.cdr())
            prt('lstarg rlst',rlst)
            lst.extend(rlst)
            prt('lstarg lst',lst)
            return lst
            
    
    def eval(self, obj, tab):
        #self.tab.update(tab)
        
        prt('@lamb eval:obj', obj.toStr())
        a = self.listArgs(self.args)
        #a = copy.deepcopy(self.arglist)
        p = 0
        nobj = obj
        #while len(a) > 0:
        while p < len(a):
            prt('@lamb eval:nobj', nobj.toStr())
            prt('@lamb eval:a',a)
            #vn = a.pop(0)
            vn = a[p]
            p += 1
            vv = nobj.car().eval(tab).val
            prt('@lamb eval:vn,vv', '{0},{1}'.format(vn,vv))
            nobj = nobj.cdr()
            c = conscell(
                sexp(atm_sym,vn,tab) , 
                conscell(
                    sexp(atm_int,vv, tab), nil ,tab), tab)
            prt('@lamb eval:c',c.toStr())
            
            self.env.let_op(c,self.tab) #local scope
            prt('@lamb eval tab',self.tab)
        
        return self.body.eval(self.tab)


#lisp = repl(gsymtab)
ltab={}
lisp = repl(ltab)

o=lisp.l


txt='(lambda (x y) (+ (* x y) (- x y)))'
#txt='(lambda (x y) (+ x y))'
#txt='(lambda (x) (+ x 1 (* x 2)))'
txa='3 2'
#txa='2'
txcl='('+txt+txa+')'
#txc='(define ltest '+txt+')'
txc='(define x (lambda (y) (* y 2)))'
txc='(define f (lambda (x y) (if (eq x y) (cons x (* y x)) (cons (* x 10) (* y 10)))))'
txc='(define fact (lambda (x) (if (eq x 0) 1 (* x (fact (- x 1))))))'
txc='(define bank-amount ((lambda (amount) (lambda (n) (set! amount (+ amount n)))) 100))'
txc ='(load "init.l")'
#txc= txcl

print(txc)

txt = txc

while True:
    #txt = lisp.readtxt()
    o = lisp.token(txt)
    #print('token:',o.toStr())
    try:
        e = lisp.eval(o)
    except:
        e=traceback.print_exc()
        pass
    #print('e:',e)
    try:
        p = lisp.printer(e)
    except:
        print(traceback.print_exc())
    
    txt = lisp.readtxt()
