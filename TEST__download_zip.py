from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile

url = "https://github.com/jezscha/avalon-app/archive/master.zip"
out_file = r"C:\Users\jezsc\Google Drive\CG-PIPE-CLINIC\avalon-app\test"

resp = urlopen(url)
zipfile = ZipFile(BytesIO(resp.read()))
zipfile.extractall(out_file)
zipfile.close()
