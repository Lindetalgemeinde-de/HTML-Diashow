from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import datetime
import base64
import sys
import os
import shutil
import ftplib
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

"""
Konfiguration
"""
SharePointServer = config['SharePoint']['SharePointServer']
SharePointGroup = config['SharePoint']['SharePointGroup']
SharePointUsername = config['SharePoint']['SharePointUsername']
SharePointPassword = config['SharePoint']['SharePointPassword'] # b64
SharePointDownloadFolder = config['SharePoint']['SharePointDownloadFolder']

FTPHost = config['FTP']['FTPHost']
FTPUsername = config['FTP']['FTPUsername']
FTPPassword = config['FTP']['FTPPassword']
FTPPath = config['FTP']['FTPPath']

"""
SharePoint Hauptklasse
"""
class SharePointSchaukasten:
  usr = ''
  pwr = ''
  week_num = 52 # Kalenderwoche
  server = ''
  server_folder = '/sites/{group}/Freigegebene%20Dokumente/Schaukasten/{week_num}'
  group = ''
  group_url = 'https://{server}.sharepoint.com/sites/{group}'
  sharepoint = '' # Sharepoint Instance
  download_folder = ''
  download_path = ''

  """
  Festlegen der Standartkonfiguration
  """
  def __init__(self):
    global SharePointServer, SharePointGroup, SharePointUsername, SharePointPassword

    self.server = SharePointServer
    self.group = SharePointGroup
    self.usr = SharePointUsername
    self.pwr = base64.b64decode(SharePointPassword).decode()
    self.download_folder = SharePointDownloadFolder

    self.week_num = self.get_calender_week()
    self.server_folder = self.server_folder.format(group = self.group, week_num = self.week_num)
    self.group_url = self.group_url.format(server = self.server, group = self.group)

  """
  Festlegen der aktuellen Kalenderwoche
  """
  def get_calender_week(self):
    week = datetime.date.today().isocalendar().week
    # Falls Kalenderwoche 53 ist, bleibt die 52 Kalenderwoche als Standart
    if week in range(1, 52):
      return week

  """
  Führt die Authentifizierung an Sharepoint durch
  """
  def sharepoint_authentication(self):
    print("[#] SharePoint Authentication")

    sharepoint_auth = AuthenticationContext(self.group_url)
    try:
      if sharepoint_auth.acquire_token_for_user(self.usr, self.pwr):
        self.sharepoint = ClientContext(self.group_url, sharepoint_auth)
        web = self.sharepoint.web
        self.sharepoint.load(web)
        self.sharepoint.execute_query()
        return True
    except:
      print(sys.exc_info())
      return False

  """
  Läd die Dateien aus dem Kalenderwochen Ordner runter
  """
  def download_files(self):
    print("[#] SharePoint Download")
    self.create_download_folder()

    for f in self.get_files_from_folder():
      print("'" + f + "' to '" + self.download_path + "'")

      response = File.open_binary(self.sharepoint, self.server_folder + '/' + f)
      with open(self.download_path + os.sep + f, "wb") as local_file:
        local_file.write(response.content)

  """
  Holt die Dateinamen aus dem Verzeichniss aus der Kalenderwoche
  """
  def get_files_from_folder(self):
    files = []
    try:
      folder = self.sharepoint.web.get_folder_by_server_relative_url(self.server_folder)
      sub_folders = folder.files
      self.sharepoint.load(sub_folders)
      self.sharepoint.execute_query()

      for f in sub_folders:
        files.append(f.properties["Name"])
      
      return files
    except:
      print(sys.exc_info())

  """
  Erstellt lokalen Download Ordner
  """
  def create_download_folder(self):
    self.download_path = self.download_folder + os.sep + str(self.week_num)
    if not os.path.exists(self.download_path):
      os.makedirs(self.download_path)

  """
  Räumt die alten Dateien weg
  """
  def clean_up(self):
    print("[#] Local Clean up")
    for d in range (1, 52):
      if d != self.week_num:
        dp = self.download_folder + os.sep + str(d).zfill(2)
        if os.path.exists(dp):
          print("Remove dir: " + dp)
          shutil.rmtree(dp)

class FTPSchaukasten:
  # ToDo: https://www.geeksforgeeks.org/how-to-download-and-upload-files-in-ftp-server-using-python/
  host = ''
  usr  = ''
  pwr  = ''
  ftp_path = ''
  ftp_server = '' # FTP Instance

  def __init__(self):
    global FTPHost, FTPUsername, FTPPassword, FTPPath

    self.host = FTPHost
    self.usr = FTPUsername
    self.pwr = base64.b64decode(FTPPassword).decode()
    self.ftp_path = FTPPath + str(Schaukasten.week_num)

    print("[#] FTP Authentication")
    self.ftp_server = ftplib.FTP(self.host, self.usr, self.pwr)
    self.cd_tree(self.ftp_path)
    self.upload_files()
    self.clean_up()

    self.ftp_server.quit()
    print("[#] FTP Logout")
  
  """
  Wechselt das Verzeichnis und erstellt es falls nicht vorhanden
  """
  def cd_tree(self, currentDir):
    if currentDir != '':
        for d in currentDir.split('/'):
          try:
            # print('Entering: {}'.format(d))
            self.ftp_server.cwd(d)
          except:
            # print('Creating: {}'.format(d))
            self.ftp_server.mkd(d)
            self.ftp_server.cwd(d)

  """
  Lädt die runtergeladenen Dateien auf den FTP Server hoch
  """
  def upload_files(self):
    print("[#] FTP Upload")
    for f in os.listdir(Schaukasten.download_path):
      ff = open(Schaukasten.download_path + os.sep + f,'rb')
      print("Upload file: " + Schaukasten.download_path + os.sep + f)
      self.ftp_server.storbinary('STOR {}'.format(f), ff)

  """
  Räumt die alten Dateien weg
  """
  def clean_up(self):
    print("[#] FTP Clean up")

    self.ftp_server.cwd('..')

    for d in self.ftp_server.nlst():
      if d != str(SharePointSchaukasten.get_calender_week(self)):
        print("Remove dir: " + d)
        try:
          self.ftp_server.rmd(d)
        except:
          self.ftp_server.cwd(d)
          for f in self.ftp_server.nlst():
            self.ftp_server.delete(f)
          self.ftp_server.cwd('..')
          self.ftp_server.rmd(d)

"""
Aufrufen der Klasse zum ausführen unseres Scripts
"""
if __name__ == '__main__':
  try:
    Schaukasten = SharePointSchaukasten()
    Schaukasten.sharepoint_authentication()
    Schaukasten.download_files()
    Schaukasten.clean_up()

    FTP = FTPSchaukasten()
  except:
    pass
