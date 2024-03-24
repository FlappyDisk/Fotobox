from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import glob

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)
path = r"E:/Programmiern/Fotobox/ImagesTest"
file_list = drive.ListFile({'q': "'1GtwuyX75loYdN62mW5t6Su2cXDNl-OiU' in parents and trashed=false"}).GetList()
title_list = []
for file in file_list:
    title_list.append(file['title'])
for filename in os.listdir(path):
    if(title_list.count(filename) == 0):
        f = drive.CreateFile({'title': filename, 'parents': [{'id': '1GtwuyX75loYdN62mW5t6Su2cXDNl-OiU'}]})
        f.SetContentFile(os.path.join(path, filename))
        f.Upload()
        f = None
