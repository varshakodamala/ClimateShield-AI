import sys
sys.path.insert(0, '.')
import services.api.main as m
print('module file', m.__file__)
print('os in module', 'os' in m.__dict__)
print('os module', m.os)

try:
    cfg = m.load_config()
    print('config loaded', cfg)
except Exception as e:
    import traceback
    traceback.print_exc()

print('call expand directly')
try:
    x = m.expand_env_vars('foo ${OPENWEATHER_API_KEY} bar')
    print('expanded', x)
except Exception as e:
    import traceback
    traceback.print_exc()
