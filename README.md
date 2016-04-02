# jupyter-pstate
Save Jupyter state inside the function and open it in other Jupyter tab.

## parent.ipynb:
```python
from jupyter_pstate import pstate
STATE = pstate('./test.tmp')

a = ''
def func1():
  global a
  a = 'imported'
  STATE.ImportBreak() # <- Stop importing as module.
  b = 'saved'
  STATE.save(locals()) # <- Save local() via pickle and stop execution.
  c = 'not executed' 
func1()
# Execution stoped.
```

## child.ipynb:
```python
from jupyter_pstate import pstate
STATE = pstate('./test.tmp')
from parent import *
print(a)
# OUT: imported
print(b)
# Traceback
locals().update(STATE.load()[0])
print(b)
# OUT: saved
# We are inisde the function: parent.func1
print(c)
# Traceback. This is never executed.
```

  
