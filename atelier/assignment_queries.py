"""Five individually presentable modules: three DML and five SELECTs each."""
def module(key, number, title, tables, table, pk, field, initial, changed, insert, selects):
    return dict(id=key, number=number, title=title, tables=tables, table=table, pk=pk, field=field,
                initial=initial, changed=changed, queries=[
        dict(id='insert',kind='INSERT',title='Create a demonstration record',sql=insert),
        dict(id='update',kind='UPDATE',title='Update that record',sql=f'UPDATE {table}\nSET {field} = :value\nWHERE {pk} = :record_id'),
        dict(id='delete',kind='DELETE',title='Delete that demonstration record',sql=f'DELETE FROM {table}\nWHERE {pk} = :record_id'),
        *[dict(id=f'select{i}',kind='SELECT',title=title,sql=sql) for i,(title,sql) in enumerate(selects,1)]])


MEMBERS = ('Vihaan', 'Kaashvi', 'Gaurav', 'Shanil', 'Ashutosh')

MODULES = [
module('collection',1,'Artists & collection','ARTIST · ARTWORK','artwork','artwork_id','title',
 'Study in Light','Study in Light revised',
 """INSERT INTO artwork (artwork_id, artist_id, title)
VALUES (:record_id, 1, :value)""",[
 ('Search artworks by title',"""SELECT artwork_id, title, medium
FROM artwork
WHERE title LIKE :search"""),
 ('Show each artwork and its artist',"""SELECT w.title, a.name
FROM artwork w
JOIN artist a ON w.artist_id = a.artist_id"""),
 ('Count artworks for each artist',"""SELECT artist_id, COUNT(*) AS total_artworks
FROM artwork
GROUP BY artist_id"""),
 ('Find artworks by Indian artists',"""SELECT title
FROM artwork
WHERE artist_id IN (
    SELECT artist_id FROM artist WHERE nationality = 'Indian'
)"""),
 ('Show artwork titles in capital letters',"""SELECT UPPER(title) AS title_in_capitals
FROM artwork""")]),
module('exhibitions',2,'Galleries & exhibitions','GALLERY · EXHIBITION','exhibition','exhibition_id','title',
 'Light and Memory','Light and Memory revised',
 """INSERT INTO exhibition
    (exhibition_id, gallery_id, curator_id, title, start_date, end_date)
VALUES (:record_id, 1, 1, :value, DATE '2026-11-01', DATE '2026-12-31')""",[
 ('Search exhibitions by title',"""SELECT exhibition_id, title, start_date, end_date
FROM exhibition
WHERE title LIKE :search"""),
 ('Show each exhibition and its gallery',"""SELECT e.title, g.name
FROM exhibition e
JOIN gallery g ON e.gallery_id = g.gallery_id"""),
 ('Count exhibitions for each gallery',"""SELECT gallery_id, COUNT(*) AS total_exhibitions
FROM exhibition
GROUP BY gallery_id"""),
 ('Find exhibitions in Mumbai galleries',"""SELECT title
FROM exhibition
WHERE gallery_id IN (
    SELECT gallery_id FROM gallery WHERE city = 'Mumbai'
)"""),
 ('Format exhibition opening dates',"""SELECT title, TO_CHAR(start_date, 'DD-MM-YYYY') AS opening_date
FROM exhibition""")]),
module('auctions',3,'Auctions & lots','AUCTION · AUCTION_LOT','auction','auction_id','title',
 'Student Auction','Student Auction revised',
 """INSERT INTO auction (auction_id, gallery_id, title, "DATE")
VALUES (:record_id, 1, :value, DATE '2026-12-15')""",[
 ('Search auctions by title',"""SELECT auction_id, title, status
FROM auction
WHERE title LIKE :search"""),
 ('Show the lots in each auction',"""SELECT a.title, l.lot_number
FROM auction a
JOIN auction_lot l ON a.auction_id = l.auction_id"""),
 ('Count lots for each auction',"""SELECT auction_id, COUNT(*) AS total_lots
FROM auction_lot
GROUP BY auction_id"""),
 ('Find lots belonging to open auctions',"""SELECT lot_id, lot_number
FROM auction_lot
WHERE auction_id IN (
    SELECT auction_id FROM auction WHERE status = 'open'
)"""),
 ('Show starting prices in rupees',"""SELECT lot_id, ROUND(starting_price / 100, 2) AS starting_price_inr
FROM auction_lot""")]),
module('bidders',4,'Bidders & bids','BIDDER · BID','bidder','bidder_id','name',
 'Demo Bidder','Demo Bidder revised',
 """INSERT INTO bidder (bidder_id, name, email)
VALUES (:record_id, :value, :email)""",[
 ('Search bidders by name',"""SELECT bidder_id, name, email
FROM bidder
WHERE name LIKE :search"""),
 ('Show bids with bidder names',"""SELECT r.name, b.bid_amount / 100 AS amount_inr
FROM bidder r
JOIN bid b ON r.bidder_id = b.bidder_id"""),
 ('Count bids for each bidder',"""SELECT bidder_id, COUNT(*) AS total_bids
FROM bid
GROUP BY bidder_id"""),
 ('Find bidders who placed a bid',"""SELECT name
FROM bidder
WHERE bidder_id IN (
    SELECT bidder_id FROM bid
)"""),
 ('Show bidder emails in lowercase',"""SELECT name, LOWER(email) AS email
FROM bidder""")]),
module('experts',5,'Experts & appraisals','ART_EXPERT · APPRAISAL','art_expert','expert_id','name',
 'Demo Expert','Demo Expert revised',
 """INSERT INTO art_expert (expert_id, name)
VALUES (:record_id, :value)""",[
 ('Search experts by name',"""SELECT expert_id, name, specialization
FROM art_expert
WHERE name LIKE :search"""),
 ('Show appraisals with expert names',"""SELECT e.name, p.estimated_value / 100 AS value_inr
FROM art_expert e
JOIN appraisal p ON e.expert_id = p.expert_id"""),
 ('Count appraisals for each expert',"""SELECT expert_id, COUNT(*) AS total_appraisals
FROM appraisal
GROUP BY expert_id"""),
 ('Find experts who performed an appraisal',"""SELECT name
FROM art_expert
WHERE expert_id IN (
    SELECT expert_id FROM appraisal
)"""),
 ('Show expert names in capital letters',"""SELECT UPPER(name) AS expert_name
FROM art_expert""")])
]

for item in MODULES:
    item['presenter'] = MEMBERS[item['number'] - 1]


EXTRA_SELECTS = [
 dict(id='set-union',title='UNION: people who participate in the art system',sql="SELECT name FROM artist UNION SELECT name FROM art_expert ORDER BY name"),
 dict(id='set-intersect',title='INTERSECT: artworks with both assessments',sql='SELECT artwork_id FROM appraisal INTERSECT SELECT artwork_id FROM authentication'),
 dict(id='set-minus',title='MINUS: artworks without authentication',sql='SELECT artwork_id FROM artwork MINUS SELECT artwork_id FROM authentication'),
 dict(id='view',title='View: completed gallery revenue',sql='SELECT gallery_id,name,paid_sales,revenue_inr FROM gallery_revenue ORDER BY gallery_id'),
 dict(id='any-all',title='ALL: appraisals at least as large as every appraisal',sql='SELECT appraisal_id,estimated_value/100 AS estimate_inr FROM appraisal WHERE estimated_value >= ALL (SELECT estimated_value FROM appraisal)'),
]


def find_module(key):
    return next((m for m in MODULES if m['id']==key),None)
