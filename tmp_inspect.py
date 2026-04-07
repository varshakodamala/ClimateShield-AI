import sys, inspect
sys.path.insert(0, '.')
import services.api.main as m
print(inspect.getsource(m.expand_env_vars))
print('os in globals?', 'os' in m.__dict__)
print('expand_env_vars glob os=', m.expand_env_vars.__globals__.get('os'))
