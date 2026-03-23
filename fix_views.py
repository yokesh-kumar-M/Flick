with open('access_service/access/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# We just need to fix lines 254-257. They currently contain literal newlines inside an f-string instead of \n.
# Actually let's just make it a multiline f-string with triple quotes.
content = re.sub(
    r"f'Your payment for(.*?)\n\nYour Unlock Hash(.*?)\n\nPlease enter(.*? forever\.',)",
    r"f'''Your payment for\1\n\nYour Unlock Hash\2\n\nPlease enter\3'''",
    content,
    flags=re.DOTALL
)

content = re.sub(
    r"f'Your payment for(.*?)\n(.*?)',",
    r"f'''Your payment for\1\n\2''',",
    content,
    flags=re.DOTALL
)

content = re.sub(
    r"f'An admin has gifted you access(.*?)\n(.*?)!',",
    r"f'''An admin has gifted you access\1\n\2!''',",
    content,
    flags=re.DOTALL
)

with open('access_service/access/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
