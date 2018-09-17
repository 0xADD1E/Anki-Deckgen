import sqlite3
import csv
import sys
import hashlib
import uuid
import os
import shutil
import util.timer
import util.anki_setup
with open(sys.argv[1]) as myFile:
    myFile.readline()
    rd = csv.reader(myFile)
    lines = [(eng, sp_m, sp_f, [tag.strip().rstrip().replace(' ','_') for tag in tags.split(';')])
             for eng, sp_m, sp_f, tags, _ in rd]
epoch_time = timer.fucked_up_timer()
if os.path.exists('anki'):
    shutil.rmtree('anki')
os.makedirs('anki')
with sqlite3.connect('anki/collection.anki2') as conn:
    anki_setup.create(conn)
    c = conn.cursor()
    deck_id = c.execute("SELECT id FROM col").fetchone()[0]
    for eng, sp_m, sp_f, tags in lines:
        n_id = epoch_time.get()
        n_guid = str(uuid.uuid4())[:8]
        n_mid = 1536800704190
        n_mod = n_id
        n_usn = -1
        n_tags = ' '+' '.join(tags)+' '

        n_sfld = "English: {{c1::"+eng+'}}<br />Spanish: {{c2::'
        if sp_m.strip():
            n_sfld += sp_m+' (masc)<br />'
        if sp_f.strip():
            n_sfld += sp_f+' (femme)<br />'
        n_sfld += '}}'
        n_flds = n_sfld+chr(0x1f)

        n_csum = str(int(hashlib.sha1(n_flds.split('\u0031')[
                     0].encode('UTF-8')).hexdigest(), 16))[:8]
        n_flags = 0
        n_data = ''
        c.execute("INSERT INTO notes VALUES (?,?,?,?,?,?,?,?,?,?,?)", (n_id, n_guid,
                                                                       n_mid, n_mod, n_usn, n_tags, n_flds, n_sfld, n_csum, n_flags, n_data))
        for i in range(2):
            c_id = epoch_time.get()
            c_nid = n_id
            c_did = deck_id
            c_ord = i
            c_mod = c_id
            c_usn = -1
            c_type = 0
            c_queue = 0
            c_due = 1
            c_ivl = 0
            c_factor = 2500
            c_reps = 0
            c_lapses = 0
            c_left = 2002
            c_odue = 0
            c_odid = 0
            c_flags = 0
            c_data = ''
            c_tuple = (c_id, c_nid, c_did, c_ord, c_mod,  c_usn, c_type, c_queue, c_due, c_ivl,
                       c_factor, c_reps, c_lapses, c_left, c_odue, c_odid, c_flags, c_data)
            c.execute(
                "INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", c_tuple)
    conn.commit()
with open('anki/media', 'w') as myFile:
    myFile.write('{}')

if os.path.exists('MyDeck.apkg'):
    os.remove('MyDeck.apkg')
shutil.make_archive('MyDeck', 'zip', 'anki')
os.rename('MyDeck.zip', 'MyDeck.apkg')
