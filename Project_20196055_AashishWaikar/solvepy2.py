import sys 
import copy
import datetime


_LOAD_FILENAME = None
_DEBUG = False
_TIMING_DEBUG = False
_TWOSIDED = True 


if not sys.argv:
  print """No arguments given....pls provide filename"""
for a in sys.argv: 
  _LOAD_FILENAME = a
  

class _DPLLSolver:

  def Reader(self, filename):
    if _DEBUG:
      print "Opening %s" % filename
    file = open(filename, 'r')
    clauses = []
    num_vars = None
    num_clauses = None
    for l in file.readlines():
      if l[0] == 'p':
        if not l[:5] == 'p cnf':
          raise Exception, "unexpected file format"
        num_vars = int(l.split()[2])
        num_clauses = int(l.split()[3])
        continue
      if l[0] == 'c' or l[0] == '0' or not l.split() or l.split()[-1] != '0':
        continue
      clause = map(int,l.split()[:-1])
      clause.sort()
      clauses.append(clause)
    if _DEBUG:
      print "len: " + str(len(clauses))
      print "num: " + str(num_clauses)
    if num_clauses != len(clauses):
      raise Exception, "error reading in cnf file"
    file.close()
    return clauses, num_vars
  
  def Parentfn(self, problem_str):
    sat = False
    outstr="v"
    start_time = datetime.datetime.now()
    if not problem_str[-4:] == ".cnf":
      problem_str = problem_str + ".cnf"
    clauses, num = self.Reader(problem_str)
    if not self.MyDPLL(clauses, num):
      print "s UNSATISFIABLE"
    else:
      sat = True
      print "s SATISFIABLE"
      sol = self.lits
      sol.sort(key=abs)
      for lit in sol:
        if lit > 0:
          outstr+=" "+str(lit)
        else:
          outstr+=" "+str(lit);
      print outstr+" 0"
    end_time = datetime.datetime.now()
    if _TIMING_DEBUG or _DEBUG:
      print "Total time (seconds): %s" % str(datetime.datetime.now()-start_time)
    return sat

  def MyDPLL(self, clauses, num_lits):
    self.num_lits = num_lits
    self.lits = []
    self.underived = []
    self.clauses = clauses
    self.lit_dict = {}
    self.last_true_index = 0
    while True:
      if len(self.lits) < num_lits:
        cls = self.filter()
        lit = self.JW(cls)
        self.lits.append(lit)
        self.underived.append(True)
        self.last_true_index = len(self.underived) - 1
        self.lit_dict[lit] = True
      val = self.UnitPropagate()
      if val == 0:
        continue
      if val == 1:
        return True
      elif val == -1:
        return False

  def UnitPropagate(self):
    clauses = copy.copy(self.clauses)
    while True:
      full_break = False
      cls = []
      for i in xrange(len(clauses)):
        c = clauses[i]
        if len(c) == 1:
          if -c[0] in self.lits:
            if self.Backtrack():
              full_break = True
              break
            else: return -1
          if not c[0] in self.lits:
            self.lits.append(c[0])
            self.underived.append(False)
            self.lit_dict[(c[0])] = True
        ccop = copy.copy(c)
        for j in xrange(len(c)):
          if c[j] in self.lit_dict: 
            break
          if -c[j] in self.lit_dict:
            ccop.remove(c[j])
            if not ccop:
              if self.Backtrack():
                full_break = True
                break
              else: return -1
          if j == len(c)-1:
            cls.append(ccop)
        if full_break:
          break
      if full_break:
        clauses = copy.copy(self.clauses)
      else:
        if len(cls) == 0:
          return 1
        if len(cls) == len(clauses) and not full_break:
          break
        clauses = cls
    return 0
        
  def Backtrack(self):
    if self.last_true_index == -1:
      return False
    self.lits = self.lits[:self.last_true_index+1]
    lit = self.lits.pop()
    self.lits.append(-lit)
    self.lit_dict = {}
    for i in xrange(len(self.lits)):
      self.lit_dict[self.lits[i]] = True 
    self.underived = self.underived[:self.last_true_index+1]
    self.underived[self.last_true_index] = False
    self.SetIndex()
    return True

  def SetIndex(self):
    for i in xrange(len(self.underived)):
      if self.underived[len(self.underived)-i-1]:
        self.last_true_index = len(self.underived)-i-1
        return
    self.last_true_index = -1

  def filter(self):
    cls = []
    for i in xrange(len(self.clauses)):
      c = self.clauses[i]
      ccop = copy.copy(c)
      for j in xrange(len(c)):
        if c[j] in self.lit_dict: 
          break
        if -c[j] in self.lit_dict:
          ccop.remove(c[j])
        if j == len(c)-1:
          cls.append(ccop)
    return cls

  def JW(self, clauses):
    if not clauses: return None
    js = {}
    max = -1
    max_lit = 0
    for i in xrange(len(clauses)):
      for lit in clauses[i]:
        if lit in js: js[lit] += 2**(-len(clauses[i]))
        else: js[lit] = 2**(-len(clauses[i]))
        if _TWOSIDED:
          if -lit not in js: js[-lit] = 0
          if (js[lit]+js[-lit]) > max:
            max = js[lit]+js[-lit]
            if js[lit] > js[-lit]: max_lit = lit
            else: max_lit = -lit
        elif js[lit] > max:
          max = js[lit]
          max_lit = lit
    if max_lit == 0:
      raise Exception, "error"
    return max_lit

def main():
  solver = _DPLLSolver()
  if _LOAD_FILENAME:
    solver.Parentfn(_LOAD_FILENAME)
  else:
    print "Please use correct format for input file ."

if __name__ == "__main__":
  main()

