import os, sys, types, inspect
from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell
import nbformat
import pickle
import warnings

class ImportBreak(ImportError):
    """Exception for breaking import"""
    pass

class NotebookFinder(object):
    """Module finder that locates IPython Notebooks"""
    def __init__(self):
	self.loaders = {}
    
    @classmethod
    def find_notebook(cls, fullname, path=None):
	"""find a notebook, given its fully qualified name and an optional path"""
	name = fullname.rsplit('.', 1)[-1]
	if not path:
	    path = ['']
	for d in path:
	    nb_path = os.path.join(d, name + ".ipynb")
	    if os.path.isfile(nb_path):
		    return nb_path
	    elif os.path.isfile(nb_path.replace("_", " ")):
		    return nb_path.replace("_", " ")
	    elif os.path.isfile(nb_path.replace("_", "-")):
		    return nb_path.replace("_", "-")
    
    def find_module(self, fullname, path=None):
	nb_path = self.find_notebook(fullname, path)
	if not nb_path:
	    return
	key = path
	if path:
	    key = os.path.sep.join(path)
	if key not in self.loaders:
	    self.loaders[key] = NotebookLoader(path)
	return self.loaders[key]

class NotebookLoader(object):
    """Module Loader for IPython Notebooks"""
    find_notebook = NotebookFinder.find_notebook
    
    def __init__(self, path=None):
	self.shell = InteractiveShell.instance()
	self.path = path
    
    def exceptImportBreak(self, mod, cells):	# module name is used in pstate.ImportBreak
	"""Transform and exec module code"""
	try:
	    for cell in cells:
		if cell.cell_type == 'code':
		    code = self.shell.input_transformer_manager.transform_cell(cell.source)
		    exec(code, mod.__dict__)
	except ImportBreak:
	    return mod
	return mod
    
    def load_module(self, fullname):
	"""import a notebook as a module"""
	path = self.find_notebook(fullname, self.path)
	nb = nbformat.read(path, as_version=4)
	mod = types.ModuleType(fullname)
	mod.__file__ = path
	mod.__loader__ = self
	mod.__dict__['get_ipython'] = get_ipython
	sys.modules[fullname] = mod
	save_user_ns = self.shell.user_ns
	self.shell.user_ns = mod.__dict__
	try:
	    mod = self.exceptImportBreak(mod, nb.cells)
	finally:
	    self.shell.user_ns = save_user_ns
	return mod

class pstate(object):
    """Saving and loading program state with pickle.
     STATE = pstate('./file_name.tmp')"""
    def __init__(self, file_name):
	self.file_name = file_name
	
    def __call__(self, file_name):
	return pstate(file_name)
    
    def save(self, *args, pause=True, import_break=True):
	"""Saving state.
	 Args:
	  *args - vars for pickle.dump
	    pause=True - stop code execution
	    import_break=True - stop code execution when importing
	 Examples:
	  file_name = STATE.save(val1, val2)
	  STATE.save(locals())"""
	if import_break:
	    self.ImportBreak()
	with open(self.file_name, 'wb') as file:
	    pickle.dump(args, file)
	if pause:
	    print('State saved in:\n{}'.format(self.file_name))
	    input("Press Enter to continue...")
	return self.file_name
    
    def load(self):
	"""Loading saved state.
	 val1, = STATE.load()
	 locals().update(STATE.load()[0])"""
	with open(self.file_name, 'rb') as file:
	    return pickle.load(file)
    
    def ImportBreak(self):
	"""Break when importing as module."""
	for stack in inspect.stack():
	    if stack[0].f_code.co_name == 'exceptImportBreak':
		warnings.warn('Breaking import in this module!', UserWarning, stacklevel=2)
		raise ImportBreak()
	return None

if __name__ == '__main__':
    pass
else:
    # Autoadd NotebookFinder when importing.
    sys.meta_path.append(NotebookFinder())
