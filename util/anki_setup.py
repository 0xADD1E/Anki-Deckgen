strings = ["""
CREATE TABLE cards (
    id              integer primary key,
      -- the epoch milliseconds of when the card was created
    nid             integer not null,--    
      -- notes.id
    did             integer not null,
      -- deck id (available in col table)
    ord             integer not null,
      -- ordinal : identifies which of the card templates it corresponds to 
      --   valid values are from 0 to num templates - 1
    mod             integer not null,
      -- modificaton time as epoch seconds
    usn             integer not null,
      -- update sequence number : used to figure out diffs when syncing. 
      --   value of -1 indicates changes that need to be pushed to server. 
      --   usn < server usn indicates changes that need to be pulled from server.
    type            integer not null,
      -- 0=new, 1=learning, 2=due, 3=filtered
    queue           integer not null,
      -- -3=sched buried, -2=user buried, -1=suspended,
      -- 0=new, 1=learning, 2=due (as for type)
      -- 3=in learning, next rev in at least a day after the previous review
    due             integer not null,
     -- Due is used differently for different card types: 
     --   new: note id or random int
     --   due: integer day, relative to the collection's creation time
     --   learning: integer timestamp
    ivl             integer not null,
      -- interval (used in SRS algorithm). Negative = seconds, positive = days
    factor          integer not null,
      -- factor (used in SRS algorithm)
    reps            integer not null,
      -- number of reviews
    lapses          integer not null,
      -- the number of times the card went from a "was answered correctly" 
      --   to "was answered incorrectly" state
    left            integer not null,
      -- of the form a*1000+b, with:
      -- b the number of reps left till graduation
      -- a the number of reps left today
    odue            integer not null,
      -- original due: only used when the card is currently in filtered deck
    odid            integer not null,
      -- original did: only used when the card is currently in filtered deck
    flags           integer not null,
      -- currently unused
    data            text not null
      -- currently unused
);
""", """
-- col contains a single row that holds various information about the collection
CREATE TABLE col (
    id              integer primary key,
      -- arbitrary number since there is only one row
    crt             integer not null,
      -- created timestamp
    mod             integer not null,
      -- last modified in milliseconds
    scm             integer not null,
      -- schema mod time: time when "schema" was modified. 
      --   If server scm is different from the client scm a full-sync is required
    ver             integer not null,
      -- version
    dty             integer not null,
      -- dirty: unused, set to 0
    usn             integer not null,
      -- update sequence number: used for finding diffs when syncing. 
      --   See usn in cards table for more details.
    ls              integer not null,
      -- "last sync time"
    conf            text not null,
      -- json object containing configuration options that are synced
    models          text not null,
      -- json array of json objects containing the models (aka Note types)
    decks           text not null,
      -- json array of json objects containing the deck
    dconf           text not null,
      -- json array of json objects containing the deck options
    tags            text not null
      -- a cache of tags used in the collection (This list is displayed in the browser. Potentially at other place)
);
""", """
-- Contains deleted cards, notes, and decks that need to be synced. 
-- usn should be set to -1, 
-- oid is the original id.
-- type: 0 for a card, 1 for a note and 2 for a deck
CREATE TABLE graves (
    usn             integer not null,
    oid             integer not null,
    type            integer not null
);
""", """
-- Notes contain the raw information that is formatted into a number of cards
-- according to the models
CREATE TABLE notes (
    id              integer primary key,
      -- epoch seconds of when the note was created
    guid            text not null,
      -- globally unique id, almost certainly used for syncing
    mid             integer not null,
      -- model id
    mod             integer not null,
      -- modification timestamp, epoch seconds
    usn             integer not null,
      -- update sequence number: for finding diffs when syncing.
      --   See the description in the cards table for more info
    tags            text not null,
      -- space-separated string of tags. 
      --   includes space at the beginning and end, for LIKE "% tag %" queries
    flds            text not null,
      -- the values of the fields in this note. separated by 0x1f (31) character.
    sfld            text not null,
      -- sort field: used for quick sorting and duplicate check
    csum            integer not null,
      -- field checksum used for duplicate check.
      --   integer representation of first 8 digits of sha1 hash of the first field
    flags           integer not null,
      -- unused
    data            text not null
      -- unused
);
""", """
-- revlog is a review history; it has a row for every review you've ever done!
CREATE TABLE revlog (
    id              integer primary key,
       -- epoch-milliseconds timestamp of when you did the review
    cid             integer not null,
       -- cards.id
    usn             integer not null,
        -- update sequence number: for finding diffs when syncing. 
        --   See the description in the cards table for more info
    ease            integer not null,
       -- which button you pushed to score your recall. 
       -- review:  1(wrong), 2(hard), 3(ok), 4(easy)
       -- learn/relearn:   1(wrong), 2(ok), 3(easy)
    ivl             integer not null,
       -- interval
    lastIvl         integer not null,
       -- last interval
    factor          integer not null,
      -- factor
    time            integer not null,
       -- how many milliseconds your review took, up to 60000 (60s)
    type            integer not null
       --  0=learn, 1=review, 2=relearn, 3=cram
);
""",
           "CREATE INDEX ix_cards_nid on cards (nid);",
           "CREATE INDEX ix_cards_sched on cards (did, queue, due);",
           "CREATE INDEX ix_cards_usn on cards (usn);",
           "CREATE INDEX ix_notes_csum on notes (csum);",
           "CREATE INDEX ix_notes_usn on notes (usn);",
           "CREATE INDEX ix_revlog_cid on revlog (cid);",
           "CREATE INDEX ix_revlog_usn on revlog (usn);"]


def create(conn):
    c = conn.cursor()
    for string in strings:
        c.execute(string)
    col_tuples = (1, 1536742800, 1537129983918, 1537129983908, 11, 0, 0, 0, 
                  '{"activeDecks": [1], "curDeck": 1, "newSpread": 0, "collapseTime": 1200, "timeLim": 0, "estTimes": true, "dueCounts": true, "curModel": "1537129983909", "nextPos": 1, "sortType": "noteFld", "sortBackwards": false, "addToCur": true, "dayLearnFirst": false, "newBury": true}', 
                  '{"1536800704190": {"did": 1537125592314, "vers": [], "name": "Cloze", "tmpls": [{"afmt": "{{cloze:Text}}<br>\\n{{Extra}}", "qfmt": "{{cloze:Text}}", "name": "Cloze", "ord": 0, "bqfmt": "", "bafmt": "", "did": null}], "latexPre": "\\\\documentclass[12pt]{article}\\n\\\\special{papersize=3in,5in}\\n\\\\usepackage[utf8]{inputenc}\\n\\\\usepackage{amssymb,amsmath}\\n\\\\pagestyle{empty}\\n\\\\setlength{\\\\parindent}{0in}\\n\\\\begin{document}\\n", "sortf": 0, "flds": [{"ord": 0, "name": "Text", "rtl": false, "font": "Arial", "sticky": false, "size": 20, "media": []}, {"ord": 1, "name": "Extra", "rtl": false, "font": "Arial", "sticky": false, "size": 20, "media": []}], "css": ".card {\\n font-family: arial;\\n font-size: 20px;\\n text-align: center;\\n color: black;\\n background-color: white;\\n}\\n\\n.cloze {\\n font-weight: bold;\\n color: blue;\\n}\\n.nightMode .cloze {\\n color: lightblue;\\n}", "mod": 1537125651, "type": 1, "tags": [], "usn": 26, "id": "1536800704190", "latexPost": "\\\\end{document}"}}',
                  '{"1": {"newToday": [0, 0], "revToday": [0, 0], "lrnToday": [0, 0], "timeToday": [0, 0], "conf": 1, "usn": 0, "desc": "", "dyn": 0, "collapsed": false, "extendNew": 10, "extendRev": 50, "id": 1, "name": "Default", "mod": 1537129983}, "1537125592314": {"timeToday": [4, 126291, 97291, 76291, 73291, 13291], "mid": "1536800704190", "extendNew": 10, "name": "Deck The Halls", "lrnToday": [4, 2, 1, 0], "dyn": 0, "desc": "", "extendRev": 50, "mod": 1537127681, "revToday": [4, 0], "usn": 30, "id": 1537125592314, "collapsed": false, "newToday": [4, 3, 2, 1], "conf": 1}}', 
                  '{"1": {"name": "Default", "new": {"delays": [1, 10], "ints": [1, 4, 7], "initialFactor": 2500, "separate": true, "order": 1, "perDay": 20, "bury": false}, "lapse": {"delays": [10], "mult": 0, "minInt": 1, "leechFails": 8, "leechAction": 0}, "rev": {"perDay": 200, "ease4": 1.3, "fuzz": 0.05, "minSpace": 1, "ivlFct": 1, "maxIvl": 36500, "bury": false, "hardFactor": 1.2}, "maxTaken": 60, "timer": 0, "autoplay": true, "replayq": true, "mod": 0, "usn": 0, "id": 1}}', 
                  '{}')

    print(col_tuples)
    c.execute("INSERT INTO col VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", col_tuples)
    conn.commit()
