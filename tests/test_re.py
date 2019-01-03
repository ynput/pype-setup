import re
import os

# value = r'//kre-p01/share/projects/_AVALON'
# value = r'\\kre-p01\share\projects\_AVALON'
# value = r'https://pype.ftrack.com'
value = r'/this/that/prd'


frward = re.compile(r'^//').search(str(value))
bckwrd = re.compile(r'^\\').search(str(value))
url = re.compile(r'://').search(str(value))

if frward:
    print(frward)
    print(os.path.normpath(str(value)))
elif bckwrd:
    print(bckwrd)
    print(str(value))
elif url:
    print(url)
    print(str(value))
else:
    print(os.path.normpath(str(value)))
