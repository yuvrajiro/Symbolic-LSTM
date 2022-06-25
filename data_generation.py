

### Generating Functions in Sympy Format
### Inspired from Using Algorithm 2 from https://ml4sci.org/assets/faseroh.pdf
from sympy import simplify
from random import randint, choice
import sympy as sp
from tqdm import tqdm
from utility import sympy_to_prefix
from sympy.abc import x

### Generating Functions in Sympy Format
### Inspired from Using Algorithm 2 from https://ml4sci.org/assets/faseroh.pdf

N = 1000000 #Number of functions to generate
Combination_Operator = [sp.Add , lambda x,y:x*sp.Pow(y , -1) , sp.Mul]
base_functions = [sp.exp,sp.log,sp.sin,sp.cos,sp.tan,sp.cot,sp.csc,sp.sec]
debug = False
f_train = open("data.train", mode='a', encoding='utf-8')
f_valid = open("data.valid", mode='a', encoding='utf-8')
f_test  = open("data.test", mode='a', encoding='utf-8')
split = [7,2,1]
for i in tqdm(range(N)):
  fun = choice(base_functions)(x)
  if debug : print(f"Initial function generated in Loop {i+1} is : {fun}")
  n = randint(1,3)  # Number of Operators to Combine
  if debug : print(f"Number of Operators Combine in Loop {i+1} is : {n}")
  for j in range(n-1):
    Operator =  choice(Combination_Operator)
    if debug : print(f" Operators Combine Choosen in Loop {i+1} in {j+1} is {Operator}")
    fun = Operator(fun , randint(1,10)*choice(base_functions)(x))
  expr = simplify(fun)
  abc = (" ".join(sympy_to_prefix(expr)) + "\t" + " ".join(sympy_to_prefix(expr.series(x,0,4).removeO())))
  if split[0] != 0:
    f_train.write(abc + "\n")
    split[0] = split[0] - 1
  elif split[1] != 0:
    f_test.write(abc + "\n")
    split[1] = split[1] - 1
  else:
    f_valid.write(abc + "\n")
    split = [7,2,1]
  if debug : print(f"Function : {sp.simplify(fun)} and Expansion : {sp.simplify(fun).series(x,0,4)}")

f_train.close()
f_valid.close()
f_test.close()

