"""A fixed, server-owned set of SELECT queries for the DBMS presentation."""
QUERIES = [
    dict(id='collection', title='Artists, artworks & galleries',
         description='Follow one-to-many creation and many-to-many gallery representation with joins.',
         sql='''SELECT w.title AS artwork, a.name AS artist,
       COALESCE(g.name, 'Independent') AS gallery, w.medium, w.status
FROM artwork w
JOIN artist a ON a.artist_id = w.artist_id
LEFT JOIN artist_gallery ag ON ag.artist_id = a.artist_id
LEFT JOIN gallery g ON g.gallery_id = ag.gallery_id
ORDER BY a.name, w.title;'''),
    dict(id='exhibitions', title='Inside an exhibition',
         description='A junction table connects each exhibition to its ordered artwork lineup.',
         sql='''SELECT e.title AS exhibition, g.name AS gallery, c.name AS curator,
       w.title AS artwork, ea.display_position
FROM exhibition e
JOIN gallery g ON g.gallery_id = e.gallery_id
JOIN curator c ON c.curator_id = e.curator_id
LEFT JOIN exhibition_artwork ea ON ea.exhibition_id = e.exhibition_id
LEFT JOIN artwork w ON w.artwork_id = ea.artwork_id
ORDER BY e.title, ea.display_position;'''),
    dict(id='bidding', title='The bidding room',
         description='LEFT JOIN and aggregation retain lots that have not received a bid.',
         sql='''SELECT a.title AS auction, l.lot_number, w.title AS artwork,
       l.status, COUNT(b.bid_id) AS bid_count,
       ROUND(MAX(b.bid_amount) / 100.0, 2) AS highest_bid_inr
FROM auction_lot l
JOIN auction a ON a.auction_id = l.auction_id
JOIN artwork w ON w.artwork_id = l.artwork_id
LEFT JOIN bid b ON b.lot_id = l.lot_id
GROUP BY a.title, a.auction_id, l.lot_id, l.lot_number, w.title, l.status
ORDER BY a.auction_id, l.lot_number;'''),
    dict(id='revenue', title='Revenue by gallery',
         description='Only completed payments contribute to revenue; galleries without revenue remain visible.',
         sql='''SELECT g.name AS gallery,
       COUNT(CASE WHEN s.payment_status = 'completed' THEN s.sale_id END) AS paid_sales,
       ROUND(COALESCE(SUM(CASE WHEN s.payment_status = 'completed'
           THEN s.sale_price ELSE 0 END), 0) / 100.0, 2) AS revenue_inr
FROM gallery g
LEFT JOIN auction a ON a.gallery_id = g.gallery_id
LEFT JOIN auction_lot l ON l.auction_id = a.auction_id
LEFT JOIN bid b ON b.lot_id = l.lot_id
LEFT JOIN sale s ON s.bid_id = b.bid_id
GROUP BY g.gallery_id, g.name
ORDER BY revenue_inr DESC;'''),
    dict(id='collectors', title='Collector spending',
         description='Total amount spent is derived from completed sales rather than stored on the collector.',
         sql='''SELECT c.name AS collector,
       COUNT(s.sale_id) AS purchases,
       ROUND(COALESCE(SUM(CASE WHEN s.payment_status = 'completed'
           THEN s.sale_price ELSE 0 END), 0) / 100.0, 2) AS total_spent_inr
FROM collector c
LEFT JOIN sale s ON s.collector_id = c.collector_id
GROUP BY c.collector_id, c.name
ORDER BY total_spent_inr DESC;'''),
    dict(id='assessments', title='Works needing a closer look',
         description='NOT EXISTS finds missing expert appraisals or authentication without multiplying history rows.',
         sql='''SELECT w.title AS artwork, a.name AS artist,
       CASE WHEN NOT EXISTS (SELECT 1 FROM appraisal p WHERE p.artwork_id = w.artwork_id)
            THEN 'Missing' ELSE 'Recorded' END AS appraisal,
       CASE WHEN NOT EXISTS (SELECT 1 FROM authentication t WHERE t.artwork_id = w.artwork_id)
            THEN 'Missing' ELSE 'Recorded' END AS authentication
FROM artwork w
JOIN artist a ON a.artist_id = w.artist_id
WHERE NOT EXISTS (SELECT 1 FROM appraisal p WHERE p.artwork_id = w.artwork_id)
   OR NOT EXISTS (SELECT 1 FROM authentication t WHERE t.artwork_id = w.artwork_id)
ORDER BY w.title;'''),
]
