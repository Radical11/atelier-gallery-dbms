from werkzeug.security import generate_password_hash
from . import services


def seed_db(conn):
    """Install demo records once, without changing existing records on later calls."""
    if conn.execute("SELECT 1 FROM user_account WHERE email='admin@atelier.example'").fetchone():
        return
    artists = [
        (1,'Amara Sen','1978-02-18','Indian','Explores memory through layered colour.'),
        (2,'Kavita Rao','1984-06-12','Indian','Paints quiet studies of urban life.'),
        (3,'Isabelle Laurent','1972-03-03','French','Works with texture and atmospheric landscapes.'),
        (4,'Noah Kim','1988-09-21','Korean','A multidisciplinary artist inspired by nature.'),
        (5,'Leila Haddad','1980-11-08','Lebanese','Uses abstraction to explore place and belonging.'),
        (6,'Mateo Alvarez','1975-05-15','Spanish','Creates luminous studies of movement and light.'),
    ]
    artworks = [
        ('Monsoon Reverie',1,2021,'Oil on canvas'),('A Quiet Morning',2,2020,'Acrylic on canvas'),
        ('Blue Distance',3,2019,'Oil on linen'),('The Golden Hour',4,2022,'Mixed media'),
        ('Garden of Echoes',5,2023,'Acrylic on canvas'),('Between Tides',6,2021,'Oil on canvas'),
        ('Window to the City',2,2024,'Watercolour'),('Soft Horizons',3,2022,'Oil on linen'),
        ('A Place to Begin',1,2023,'Mixed media'),('Wild Geometry',5,2020,'Acrylic on canvas'),
        ('Evening Passage',6,2024,'Oil on canvas'),('The Light Within',4,2021,'Watercolour'),
    ]
    try:
        for aid,name,birth,nationality,bio in artists:
            conn.execute('INSERT OR IGNORE INTO artist(artist_id,name,birth_date,nationality,biography) VALUES(?,?,?,?,?)',(aid,name,birth,nationality,bio))
        for i,(title,aid,year,medium) in enumerate(artworks,1):
            conn.execute('INSERT OR IGNORE INTO artwork(artwork_id,artist_id,title,year_created,medium,dimensions,description,image_path) VALUES(?,?,?,?,?,?,?,?)', (i,aid,title,year,medium,'80 × 60 cm',f'{title} brings a distinctive contemporary perspective to the collection.',f'images/artwork-{i:02}.webp'))
        conn.executemany('INSERT OR IGNORE INTO gallery VALUES(?,?,?,?,?,?)',[(1,'Atelier Mumbai','18 Kala Ghoda','Mumbai','India','hello@atelier.example'),(2,'Atelier Delhi','42 Lodhi Road','New Delhi','India','delhi@atelier.example')])
        conn.executemany('INSERT OR IGNORE INTO curator VALUES(?,?,?,?)',[(1,'Riya Mehta','riya@atelier.example','+91 90000 10001'),(2,'Omar Shah','omar@atelier.example','+91 90000 10002'),(3,'Isha Kapoor','isha@atelier.example','+91 90000 10003')])
        conn.executemany('INSERT OR IGNORE INTO exhibition VALUES(?,?,?,?,?,?,?)',[(1,1,1,'Colour and Memory','2026-10-01','2026-12-20','Contemporary stories in colour'),(2,2,2,'Quiet Places','2026-11-01','2027-01-15','Landscapes and stillness'),(3,1,3,'New Perspectives','2027-02-01','2027-03-31','Emerging contemporary art')])
        conn.executemany('INSERT OR IGNORE INTO art_expert VALUES(?,?,?,?,?)',[(1,'Dr. Anika Desai','Modern painting','anika@atelier.example','+91 90000 20001'),(2,'Daniel Roy','Contemporary art','daniel@atelier.example','+91 90000 20002')])
        conn.executemany('INSERT OR IGNORE INTO bidder VALUES(?,?,?,?,?)',[(1,'Maya Sharma','maya@atelier.example','+91 90000 30001','Mumbai'),(2,'Arjun Patel','arjun@atelier.example','+91 90000 30002','Delhi'),(3,'Sara Khan','sara@atelier.example','+91 90000 30003','Pune')])
        snapshot_date = conn.execute("SELECT date('now')").fetchone()[0]
        conn.executemany('INSERT OR IGNORE INTO auction VALUES(?,?,?,?,?,?,?)',[(1,1,'Autumn Contemporary','2026-11-15','Atelier Mumbai','A selection of contemporary voices.','draft'),(2,2,'Winter Preview','2026-12-12','Atelier Delhi','An upcoming collection.','draft'),(3,1,'Recent Acquisitions',snapshot_date,'Atelier Mumbai','A recent auction.','draft')])
        lots = [(101,1,4,1,5000000,6500000),(102,1,5,2,3000000,4000000),(201,2,6,1,4500000,5500000),(202,2,7,2,2500000,3500000),(301,3,1,1,4000000,5000000),(302,3,2,2,3000000,4000000),(303,3,3,3,2000000,6000000)]
        conn.executemany('INSERT OR IGNORE INTO auction_lot(lot_id,auction_id,artwork_id,lot_number,starting_price,reserve_price) SELECT ?,?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM auction_lot WHERE lot_id=?)', [lot + (lot[0],) for lot in lots])
        conn.executemany('INSERT OR IGNORE INTO artist_gallery VALUES(?,?,?,?,?)',[(1,1,'2020-01-01',None,20),(2,1,'2021-01-01',None,15),(3,2,'2022-01-01',None,18),(4,1,'2022-06-01',None,20),(5,2,'2023-01-01',None,15),(6,2,'2021-04-01',None,20)])
        conn.executemany('INSERT OR IGNORE INTO exhibition_artwork VALUES(?,?,?)',[(1,4,'Gallery A'),(1,5,'Gallery B'),(1,9,'Gallery C'),(2,8,'North wall'),(2,11,'South wall'),(3,10,'Gallery A'),(3,12,'Gallery B')])
        conn.executemany('INSERT OR IGNORE INTO appraisal VALUES(?,?,?,?,?,?)',[(1,1,1,'2026-06-01',6500000,'Condition reviewed.'),(2,4,2,'2026-09-01',8000000,'Contemporary work.')])
        conn.executemany('INSERT OR IGNORE INTO authentication VALUES(?,?,?,?,?,?,?)',[(1,1,1,'AT-001','2026-06-01','Authentic','Certificate issued.'),(2,4,2,'AT-002','2026-09-01','Authentic','Certificate issued.')])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    for auction_id in (1,3):
        if conn.execute('SELECT status FROM auction WHERE auction_id=?',(auction_id,)).fetchone()['status']=='draft':
            services.open_auction(conn,auction_id)
    for lot_id, entries in [(101,[(1,5000000),(2,5500000)]),(102,[(2,3000000),(1,3500000)]),(301,[(2,4000000),(1,5500000)]),(302,[(1,3000000),(2,4500000)]),(303,[(1,2000000),(2,2500000)])]:
        if conn.execute('SELECT status FROM auction_lot WHERE lot_id=?',(lot_id,)).fetchone()['status']=='open' and not conn.execute('SELECT 1 FROM bid WHERE lot_id=?',(lot_id,)).fetchone():
            for bidder_id,amount in entries:
                services.place_bid(conn,lot_id,bidder_id,amount)
    for lot_id in (301,302,303):
        services.close_lot(conn,lot_id)
    maya_sale = conn.execute('SELECT s.sale_id FROM sale s JOIN bid b ON b.bid_id=s.bid_id WHERE b.lot_id=301').fetchone()
    if maya_sale:
        services.update_payment(conn,maya_sale['sale_id'],'completed')
    accounts = [(1,'admin@atelier.example','AdminDemo!2026','staff',None),(2,'maya@atelier.example','BidderDemo!2026','bidder',1),(3,'arjun@atelier.example','BidderDemo!2026','bidder',2),(4,'sara@atelier.example','BidderDemo!2026','bidder',3)]
    try:
        for uid,email,password,role,bidder_id in accounts:
            conn.execute('INSERT OR IGNORE INTO user_account VALUES(?,?,?,?,?)',(uid,email,generate_password_hash(password),role,bidder_id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
