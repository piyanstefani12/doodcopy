from pymongo import MongoClient
import requests as req
import time
import os
import config
from bs4 import BeautifulSoup as bs



def create_folder(nama_folder):
    client = MongoClient(config.MONGO_URL)
    db = client['doodstream']
    collection = db['create_folder']
    insert = collection.insert_one(req.get('https://doodapi.com/api/folder/create?key='+ config.API_KEY + '&name='+ nama_folder).json())
    print(f'Berhasil Membuat Folder disimpan di Database : {insert.inserted_id}')
    print("Menuju Langkah Selanjutnya. Silakan Masukkan Link Anda...")
    client.close()

def upload():
    # Variabel MongoDB
    client = MongoClient(config.MONGO_URL)
    db = client['doodstream']
    folder = db['create_folder']
    link = db['link_sementara']
    # fld_id = folder.find({"result": {"fld_id": 1}})
    query_folder = folder.find({"result.fld_id": {"$gt": "1"}})
    query_link = link.find()
    print("Mengirim Video ke Akun Anda...")
    time.sleep(5)
    print("Silahkan Setting Folder Anda Menjadi Publik....")
    for i in query_folder:
        for y in query_link:
            req.get(f'https://doodapi.com/api/upload/url?key={config.API_KEY}&fld_id={i.get("result").get("fld_id")}&url={y.get("link")}')
    client.close()

    # Variabel MongoDB


def extract_link(linknya):
    # Connect to MongoDB
    client = MongoClient(config.MONGO_URL)
    db = client['doodstream']
    collection = db['link_sementara']
    # End Connect

    # Insert To Mongodb
    page = req.get(linknya)
    soup = bs(page.content, 'html.parser')
    link = soup.find_all("a", {"class": "btn-default"})
    print("Mencoba Membuat Link Baru di Akun Anda....")
    print("Proses Ini Memakan Waktu Beberapa Saat....")
    for i in link:
        if i['href'][0:5] == "https":
            collection.insert_one({'link' : i['href']})
    client.close()

def delete_data(folder_collection, link_collection):
    client = MongoClient(config.MONGO_URL)
    db = client['doodstream']
    folder = db[folder_collection]
    link = db[link_collection]
    print("Menyelesaikan Upload...")
    link.drop()
    folder.drop()
    os.system('cls')
    print("Proses Sudah Selesai, Data Sudah Berhasil Dihapus....")
    client.close()

def kirim_telegram():
    client = MongoClient(config.MONGO_URL)
    db = client['doodstream']
    folder = db['create_folder']
    link = db['link_sementara']
    # fld_id = folder.find({"result": {"fld_id": 1}})
    query_folder = folder.find({"result.fld_id": {"$gt": "1"}})
    query_nama = folder.find()
    print("Mencoba Kirim Telegram....")
    for i in query_nama:
        nama_folder = i.get("result").get("name")
        link_folder = i.get("result").get("code")
        req.post(f'https://api.telegram.org/bot{config.BOT_API}/sendMessage?chat_id={config.CHANNEL_ID}&text={nama_folder}\n\nhttps://d000d.com/f/{link_folder}')
    print("Pesan Sudah Dikirim, Silahkan Cek Tujuan Anda...")

def main():
    statement = input("Apakah Anda Ingin Memulai?Y/N: ")
    while statement == "Y":
        print("==============\nSelamat Datang\n==============")
        folder = input("Masukkan Nama Folder : ")
        create_folder(nama_folder=folder)
        link = input("Masukkan Link Dood: ")
        extract_link(linknya=link)
        print("Tunggu Sebentar")
        time.sleep(2)
        upload()
        kirim_telegram()
        delete_data(folder_collection='create_folder', link_collection='link_sementara')
        main()
        os.system("cls")
        if statement != "Y":
            print("Sudah Yaa")
            break

if __name__ == '__main__':
    main()