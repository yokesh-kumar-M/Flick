import glob
import re

dockerfiles = glob.glob('*/Dockerfile')

for path in dockerfiles:
    with open(path, 'r') as f:
        content = f.read()
    
    # replace 0.0.0.0:<port> with 0.0.0.0:${PORT:-<port>}
    content = re.sub(
        r'0\.0\.0\.0:(\d+)',
        r'0.0.0.0:$${PORT:-\g<1>}',
        content
    )
    # The shell string is passed directly, so we just want ${PORT:-8000} without double $$.
    content = content.replace('$${PORT', '${PORT')

    with open(path, 'w') as f:
        f.write(content)
    print(f"Fixed {path}")
