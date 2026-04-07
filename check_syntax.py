import pathlib
import py_compile

root = pathlib.Path('.').resolve()
errors = []
for p in sorted(root.rglob('*.py')):
    sp = str(p)
    if '.venv' in sp.lower() or 'site-packages' in sp.lower():
        continue
    try:
        py_compile.compile(sp, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append((sp, str(e)))

if not errors:
    print('ALL_OK')
else:
    print('ERRORS_FOUND')
    for f, m in errors:
        print('FILE:', f)
        print(m)
        print('---')
