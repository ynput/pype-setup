import re

path = r'C:\Program Files\Nuke11.2v3\Nuke11.2.exe'
# version_compile = r'(\d+[.]\d[v]\d)'
version_compile = r'(?P<version>\d+[.]\d[v]\d)'
compile = re.compile(version_compile)
version_match = compile.search(path)

print(version_match.group())
print("{version}".format(version=version_match.group()))
print("My name is {0:20}.".format('Fred'))
print("{foo[1]}".format(foo="Hello"))

# import string
#
#
# class SliceFormatter(string.Formatter):
#
#     def get_value(self, key, args, kwds):
#         if '[' in key:
#             try:
#                 print(key)
#                 key, indexes = key.split('[')
#                 indexes = map(int, indexes.split(','))
#                 if key.isdigit():
#                     return args[int(key)][slice(*indexes)]
#                 return kwds[key][slice(*indexes)]
#             except KeyError:
#                 return kwds.get(key, 'Missing')
#         return super(SliceFormatter, self).get_value(key, args, kwds)
#
#
# phrase = "Hello {name[0,5]}, nice to meet you.  I am {name[6,9]}.  That is {0[0,4]}."
# fmt = SliceFormatter()
