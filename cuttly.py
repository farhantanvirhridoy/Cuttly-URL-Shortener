import urllib
import requests
import json
import sqlite3
import tabulate


def delete(ids):
    conn = sqlite3.connect('TestDB.db')
    cur = conn.cursor()
    for id in ids.split(','):
        cur.execute(f"DELETE FROM link WHERE ID = '{id}'")
    with conn:
        cur.execute("SELECT * FROM link")
    dataset = cur.fetchall()
    header = ['ID','Date','Short Link','Full Link','Title']
    rows =  [x for x in dataset]
    print(tabulate.tabulate(rows, header,tablefmt = 'rst'))
    conn.commit()
    conn.close()


def database():
    conn = sqlite3.connect('TestDB.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS link
                 (ID text,date text, short text, full text, title text)''')
    with conn:
        cur.execute("SELECT * FROM link")
    dataset = cur.fetchall()
    header = ['ID','Date','Short Link','Full Link','Title']
    rows =  [x for x in dataset]
    print(tabulate.tabulate(rows, header,tablefmt = 'rst'))
    conn.close()
    res = input('\n\n[1] Delete some links\n[2] Analysis a link\n[3] Exit\nEnter option: ')
    if res == '1':
        ids = input('Enter IDs [separated by comma]: ')
        delete(ids)
    elif res == '2':
        id = input('Enter ID: ')
        analysis(id)
    else:
        print('Thank you')


def analysis(id):
    conn = sqlite3.connect('TestDB.db')
    cur = conn.cursor()
    
    cur.execute(f"SELECT short FROM link WHERE ID = '{id}'")
    
    dataset = cur.fetchone()
    url = (dataset[0])
    key = '0ef5caba857b8a70d576950b7ec3e1f90f517'
    try:
        r = requests.get('http://cutt.ly/api/api.php?key={}&stats={}'.format(key, url))
    except:
        print('\nYou are offline. Please check your internet connection\n')
        exit()
    y = json.loads(r.text)
    header = ['Parameter', 'Value']
    rows = []
    for k,v in y['stats'].items():        
        rows.append([k,v])
    
    print(tabulate.tabulate(rows, header,tablefmt = 'rst'))
    conn.close()


def shorten():
    link = input('Enter URL to shorten: ')
    p = urllib.parse.urlparse(link, 'http')
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ''
    if not netloc.startswith('www.'):
        netloc = 'www.' + netloc
    
    p = urllib.parse.ParseResult('http', netloc, path, *p[3:])
    
    
    key = '0ef5caba857b8a70d576950b7ec3e1f90f517'
    try:
        r = requests.get('http://cutt.ly/api/api.php?key={}&short={}'.format(key, p.geturl()))
    except:
        print('\nYou are offline. Please check your internet connection\n')
        exit()
    y = json.loads(r.text)

    conn = sqlite3.connect('TestDB.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS link
                 (ID text,date text, short text, full text, title text)''')

    
    if y["url"]["status"] == 7:
        date = y["url"]["date"]
        short = y["url"]["shortLink"]
        full = y["url"]["fullLink"]
        title = y["url"]["title"]
        with conn:
            cur.execute("SELECT * FROM link")
        dataset = cur.fetchall()
        
        i = dataset[-1][0]+1
        cur.execute(f"INSERT INTO link VALUES ('{i}','{date}','{short}','{full}','{title}')")
        print('Short Link: ',short)
        
    elif y["url"]["status"]==1: print('the shortened link comes from the domain that shortens the link, i.e. the link has already been shortened')
    elif y["url"]["status"]==2: print('the entered link is not a link')
    elif y["url"]["status"]==3: print('the preferred link name is already taken')
    elif y["url"]["status"]==4: print('Invalid API key')
    elif y["url"]["status"]==5: print('the link has not passed the validation. Includes invalid characters')
    elif y["url"]["status"]==6: print('The link provided is from a blocked domain')
    conn.commit()
    conn.close()


def main():
    
    print('''   ____      _   _   _         _   _ ____  _     
  / ___|   _| |_| |_| |_   _  | | | |  _ \| |    
 | |  | | | | __| __| | | | | | | | | |_) | |    
 | |__| |_| | |_| |_| | |_| | | |_| |  _ <| |___ 
  \____\__,_|\__|\__|_|\__, |  \___/|_| \_\_____|
  ____  _              |___/                     
 / ___|| |__   ___  _ __| |_ ___ _ __   ___ _ __ 
 \___ \| '_ \ / _ \| '__| __/ _ \ '_ \ / _ \ '__|
  ___) | | | | (_) | |  | ||  __/ | | |  __/ |   
 |____/|_| |_|\___/|_|   \__\___|_| |_|\___|_|   
                                                 ''')
    
    print('=======================By @Farhan Tanvir Hridoy')
    option = input('[1] Show database\n[2] To shorten a link\nEnter option: ')
    if option == '1':
        database()
    elif option == '2':
        shorten()


main()
