-- ATELIER: COMPLETE DATABASE SQL, COMMENTED FOR STUDY
-- Readable companion to atelier/schema.sql; the application uses that original file.
-- Contains the same table definitions, triggers and indexes; no database is executed or changed here.
-- Money: integer paise (100 paise = INR 1). Dates: ISO YYYY-MM-DD text.
-- PRAGMA below must also be enabled on every SQLite connection.

PRAGMA foreign_keys = ON;

-- ARTIST: Artist master data. Life dates are optional; death cannot precede birth.
CREATE TABLE IF NOT EXISTS artist (
    artist_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    birth_date TEXT CHECK(birth_date IS NULL OR (date(birth_date,'+0 days') IS NOT NULL AND date(birth_date,'+0 days')=birth_date)),
    death_date TEXT CHECK(death_date IS NULL OR (date(death_date,'+0 days') IS NOT NULL AND date(death_date,'+0 days')=death_date)),
    nationality TEXT,
    biography TEXT,
    CHECK(death_date IS NULL OR birth_date IS NULL OR death_date>=birth_date)
);

-- ARTWORK: Each artwork must reference one artist. Status and image reference support the application.
CREATE TABLE IF NOT EXISTS artwork (
    artwork_id INTEGER PRIMARY KEY,
    artist_id INTEGER NOT NULL REFERENCES artist ON DELETE RESTRICT,
    title TEXT NOT NULL,
    year_created INTEGER,
    medium TEXT,
    dimensions TEXT,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available','at_auction','sold')),
    image_path TEXT
);

-- GALLERY: Gallery master data used by exhibitions, auctions and artist representation.
CREATE TABLE IF NOT EXISTS gallery (
    gallery_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    country TEXT,
    contact_info TEXT
);

-- CURATOR: Curator master data. A curator can manage multiple exhibitions.
CREATE TABLE IF NOT EXISTS curator (
    curator_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT
);

-- EXHIBITION: Each exhibition requires one gallery and one curator. Dates must be valid and ordered.
CREATE TABLE IF NOT EXISTS exhibition (
    exhibition_id INTEGER PRIMARY KEY,
    gallery_id INTEGER NOT NULL REFERENCES gallery ON DELETE RESTRICT,
    curator_id INTEGER NOT NULL REFERENCES curator ON DELETE RESTRICT,
    title TEXT NOT NULL,
    start_date TEXT NOT NULL CHECK(date(start_date,'+0 days') IS NOT NULL AND date(start_date,'+0 days')=start_date),
    end_date TEXT NOT NULL CHECK(date(end_date,'+0 days') IS NOT NULL AND date(end_date,'+0 days')=end_date),
    theme TEXT,
    CHECK(end_date>=start_date)
);

-- AUCTION: Each auction requires an organizing gallery and follows draft/open/closed states.
CREATE TABLE IF NOT EXISTS auction (
    auction_id INTEGER PRIMARY KEY,
    gallery_id INTEGER NOT NULL REFERENCES gallery ON DELETE RESTRICT,
    title TEXT NOT NULL,
    date TEXT NOT NULL CHECK(date(date,'+0 days') IS NOT NULL AND date(date,'+0 days')=date),
    venue TEXT,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','open','closed'))
);

-- AUCTION_LOT: One artwork listing in one auction. Amounts are integer paise; lot number and artwork are unique within an auction.
CREATE TABLE IF NOT EXISTS auction_lot (
    lot_id INTEGER PRIMARY KEY,
    auction_id INTEGER NOT NULL REFERENCES auction ON DELETE RESTRICT,
    artwork_id INTEGER NOT NULL REFERENCES artwork ON DELETE RESTRICT,
    lot_number INTEGER NOT NULL CHECK(lot_number>0),
    starting_price INTEGER NOT NULL CHECK(typeof(starting_price)='integer' AND starting_price>=0),
    reserve_price INTEGER NOT NULL CHECK(typeof(reserve_price)='integer' AND reserve_price>=0),
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','open','sold','unsold')),
    UNIQUE(auction_id,artwork_id),
    UNIQUE(auction_id,lot_number)
);

-- Partial unique index: an artwork can have only one currently open lot.
CREATE UNIQUE INDEX IF NOT EXISTS one_active_artwork_lot ON auction_lot(artwork_id) WHERE status='open';

-- BIDDER: Participants who can place bids; each email is unique.
CREATE TABLE IF NOT EXISTS bidder (
    bidder_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT
);

-- BID: Accepted offers linked to a lot and bidder. Triggers below validate and preserve history.
CREATE TABLE IF NOT EXISTS bid (
    bid_id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL REFERENCES auction_lot ON DELETE RESTRICT,
    bidder_id INTEGER NOT NULL REFERENCES bidder ON DELETE RESTRICT,
    bid_amount INTEGER NOT NULL CHECK(typeof(bid_amount)='integer' AND bid_amount>=0),
    bid_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- COLLECTOR: Buyer profile with a unique link to the bidder identity. Contact fields are retained from the supplied domain model.
CREATE TABLE IF NOT EXISTS collector (
    collector_id INTEGER PRIMARY KEY,
    bidder_id INTEGER NOT NULL UNIQUE REFERENCES bidder ON DELETE RESTRICT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT
);

-- SALE: A sale references one unique winning bid and one collector. Its price is validated against the winning offer.
CREATE TABLE IF NOT EXISTS sale (
    sale_id INTEGER PRIMARY KEY,
    bid_id INTEGER NOT NULL UNIQUE REFERENCES bid ON DELETE RESTRICT,
    collector_id INTEGER NOT NULL REFERENCES collector ON DELETE RESTRICT,
    sale_price INTEGER NOT NULL CHECK(typeof(sale_price)='integer' AND sale_price>=0),
    sale_date TEXT NOT NULL CHECK(date(sale_date,'+0 days') IS NOT NULL AND date(sale_date,'+0 days')=sale_date),
    payment_status TEXT NOT NULL DEFAULT 'pending' CHECK(payment_status IN ('pending','completed'))
);

-- ART_EXPERT: Experts are independent entities so their details need not be repeated in each assessment.
CREATE TABLE IF NOT EXISTS art_expert (
    expert_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    specialization TEXT,
    email TEXT,
    phone TEXT
);

-- APPRAISAL: An artwork assessment performed by one expert, with estimated value in paise.
CREATE TABLE IF NOT EXISTS appraisal (
    appraisal_id INTEGER PRIMARY KEY,
    artwork_id INTEGER NOT NULL REFERENCES artwork ON DELETE RESTRICT,
    expert_id INTEGER NOT NULL REFERENCES art_expert ON DELETE RESTRICT,
    appraisal_date TEXT NOT NULL CHECK(date(appraisal_date,'+0 days') IS NOT NULL AND date(appraisal_date,'+0 days')=appraisal_date),
    estimated_value INTEGER NOT NULL CHECK(typeof(estimated_value)='integer' AND estimated_value>=0),
    notes TEXT
);

-- AUTHENTICATION: Artwork certification by an expert. This is unrelated to website login authentication.
CREATE TABLE IF NOT EXISTS authentication (
    authentication_id INTEGER PRIMARY KEY,
    artwork_id INTEGER NOT NULL REFERENCES artwork ON DELETE RESTRICT,
    expert_id INTEGER NOT NULL REFERENCES art_expert ON DELETE RESTRICT,
    certificate_no TEXT NOT NULL UNIQUE,
    authentication_date TEXT NOT NULL CHECK(date(authentication_date,'+0 days') IS NOT NULL AND date(authentication_date,'+0 days')=authentication_date),
    result TEXT NOT NULL,
    notes TEXT
);

-- ARTIST_GALLERY: Many-to-many representation. The composite primary key prevents duplicate artist/gallery pairs.
CREATE TABLE IF NOT EXISTS artist_gallery (
    artist_id INTEGER NOT NULL REFERENCES artist ON DELETE RESTRICT,
    gallery_id INTEGER NOT NULL REFERENCES gallery ON DELETE RESTRICT,
    start_date TEXT NOT NULL CHECK(date(start_date,'+0 days') IS NOT NULL AND date(start_date,'+0 days')=start_date),
    end_date TEXT CHECK(end_date IS NULL OR (date(end_date,'+0 days') IS NOT NULL AND date(end_date,'+0 days')=end_date)),
    commission_percentage REAL NOT NULL CHECK(commission_percentage BETWEEN 0 AND 100),
    PRIMARY KEY(artist_id,gallery_id),
    CHECK(end_date IS NULL OR end_date>=start_date)
);

-- EXHIBITION_ARTWORK: Many-to-many display membership. The composite primary key prevents duplicate exhibition/artwork pairs.
CREATE TABLE IF NOT EXISTS exhibition_artwork (
    exhibition_id INTEGER NOT NULL REFERENCES exhibition ON DELETE RESTRICT,
    artwork_id INTEGER NOT NULL REFERENCES artwork ON DELETE RESTRICT,
    display_position TEXT,
    PRIMARY KEY(exhibition_id,artwork_id)
);

-- USER_ACCOUNT: Website login table. Password hashes are stored; the role must agree with whether a bidder link is present.
CREATE TABLE IF NOT EXISTS user_account (
    user_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('staff','bidder')),
    bidder_id INTEGER UNIQUE REFERENCES bidder ON DELETE RESTRICT,
    CHECK((role='staff' AND bidder_id IS NULL) OR (role='bidder' AND bidder_id IS NOT NULL))
);

-- Reject bids on a closed/draft lot or auction, below starting price, or not higher than existing accepted bids.
CREATE TRIGGER IF NOT EXISTS validate_bid BEFORE INSERT ON bid BEGIN
 SELECT CASE WHEN NOT EXISTS (SELECT 1 FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=NEW.lot_id AND l.status='open' AND a.status='open' AND NEW.bid_amount>=l.starting_price) THEN RAISE(ABORT,'Lot is not open or bid is below starting price') END;
 SELECT CASE WHEN EXISTS (SELECT 1 FROM bid WHERE lot_id=NEW.lot_id AND bid_amount>=NEW.bid_amount) THEN RAISE(ABORT,'Bid must exceed current highest bid') END;
END;

-- Accepted bid history cannot be edited.
CREATE TRIGGER IF NOT EXISTS bid_no_update BEFORE UPDATE ON bid BEGIN SELECT RAISE(ABORT,'Bid history is immutable'); END;

-- Accepted bid history cannot be deleted.
CREATE TRIGGER IF NOT EXISTS bid_no_delete BEFORE DELETE ON bid BEGIN SELECT RAISE(ABORT,'Bid history is immutable'); END;

-- Require the highest reserve-meeting bid, matching buyer identity and exact amount, with no prior sale for this lot.
CREATE TRIGGER IF NOT EXISTS validate_sale BEFORE INSERT ON sale BEGIN
 SELECT CASE WHEN NOT EXISTS (SELECT 1 FROM bid b JOIN auction_lot l ON l.lot_id=b.lot_id JOIN collector c ON c.collector_id=NEW.collector_id WHERE b.bid_id=NEW.bid_id AND l.status='open' AND c.bidder_id=b.bidder_id AND NEW.sale_price=b.bid_amount AND b.bid_amount>=l.reserve_price AND NOT EXISTS (SELECT 1 FROM bid higher WHERE higher.lot_id=b.lot_id AND higher.bid_amount>b.bid_amount) AND NOT EXISTS (SELECT 1 FROM sale s JOIN bid sb ON sb.bid_id=s.bid_id WHERE sb.lot_id=b.lot_id)) THEN RAISE(ABORT,'Sale must match the winning bid and collector') END;
END;

-- Finalized sale identity, amount and date cannot be changed. Payment status can still change.
CREATE TRIGGER IF NOT EXISTS sale_immutable BEFORE UPDATE OF bid_id,collector_id,sale_price,sale_date ON sale BEGIN SELECT RAISE(ABORT,'Sale details are immutable'); END;

-- Finalized sale history cannot be deleted.
CREATE TRIGGER IF NOT EXISTS sale_no_delete BEFORE DELETE ON sale BEGIN SELECT RAISE(ABORT,'Sale history is immutable'); END;

-- A closed lot cannot be changed.
CREATE TRIGGER IF NOT EXISTS closed_lot_no_update BEFORE UPDATE ON auction_lot WHEN OLD.status IN ('sold','unsold') BEGIN SELECT RAISE(ABORT,'Closed lots are immutable'); END;

-- A closed lot cannot be removed.
CREATE TRIGGER IF NOT EXISTS closed_lot_no_delete BEFORE DELETE ON auction_lot WHEN OLD.status IN ('sold','unsold') BEGIN SELECT RAISE(ABORT,'Closed lots are immutable'); END;

-- New lots must start in draft state.
CREATE TRIGGER IF NOT EXISTS lot_insert_draft BEFORE INSERT ON auction_lot WHEN NEW.status <> 'draft' BEGIN SELECT RAISE(ABORT,'New lots must be draft'); END;

-- A draft lot can open only in an open auction and with an available artwork.
CREATE TRIGGER IF NOT EXISTS lot_open_guard BEFORE UPDATE OF status ON auction_lot WHEN NEW.status='open' AND OLD.status<>'open' BEGIN
 SELECT CASE WHEN OLD.status<>'draft' OR NOT EXISTS (SELECT 1 FROM auction a JOIN artwork w ON w.artwork_id=NEW.artwork_id WHERE a.auction_id=NEW.auction_id AND a.status='open' AND w.status='available') THEN RAISE(ABORT,'Only available draft lots can open') END;
END;

-- Sold/unsold outcome must agree with whether a sale exists.
CREATE TRIGGER IF NOT EXISTS lot_close_guard BEFORE UPDATE OF status ON auction_lot WHEN NEW.status IN ('sold','unsold') AND OLD.status='open' BEGIN
 SELECT CASE WHEN (NEW.status='sold') <> EXISTS (SELECT 1 FROM sale s JOIN bid b ON b.bid_id=s.bid_id WHERE b.lot_id=OLD.lot_id) THEN RAISE(ABORT,'Lot status must match its sale') END;
END;

-- Only draft-to-open and open-to-sold/unsold transitions are permitted.
CREATE TRIGGER IF NOT EXISTS lot_status_guard BEFORE UPDATE OF status ON auction_lot WHEN NEW.status<>OLD.status AND NOT (OLD.status='draft' AND NEW.status='open' OR OLD.status='open' AND NEW.status IN ('sold','unsold')) BEGIN SELECT RAISE(ABORT,'Invalid lot status transition'); END;

-- Freeze lot identity and pricing once bidding has opened.
CREATE TRIGGER IF NOT EXISTS lot_open_details_immutable BEFORE UPDATE OF auction_id,artwork_id,lot_number,starting_price,reserve_price ON auction_lot WHEN OLD.status='open' BEGIN SELECT RAISE(ABORT,'Open lot details are immutable'); END;

-- Only draft-to-open and open-to-closed auction transitions are permitted.
CREATE TRIGGER IF NOT EXISTS auction_status_guard BEFORE UPDATE OF status ON auction WHEN NEW.status<>OLD.status AND NOT (OLD.status='draft' AND NEW.status='open' OR OLD.status='open' AND NEW.status='closed') BEGIN SELECT RAISE(ABORT,'Invalid auction status transition'); END;

-- An auction cannot close until all its lots have finished.
CREATE TRIGGER IF NOT EXISTS auction_close_guard BEFORE UPDATE OF status ON auction WHEN NEW.status='closed' AND EXISTS (SELECT 1 FROM auction_lot WHERE auction_id=OLD.auction_id AND status IN ('draft','open')) BEGIN SELECT RAISE(ABORT,'Close all lots first'); END;

-- Lots can only be added to draft auctions.
CREATE TRIGGER IF NOT EXISTS lot_insert_auction_draft BEFORE INSERT ON auction_lot WHEN NOT EXISTS (SELECT 1 FROM auction WHERE auction_id=NEW.auction_id AND status='draft') BEGIN SELECT RAISE(ABORT,'Lots can only be added to draft auctions'); END;

-- Open lots must be retained during bidding.
CREATE TRIGGER IF NOT EXISTS open_lot_no_delete BEFORE DELETE ON auction_lot WHEN OLD.status='open' BEGIN SELECT RAISE(ABORT,'Open lots cannot be deleted'); END;
-- Index foreign-key joins and the most common per-work and per-lot history lookups.
CREATE INDEX IF NOT EXISTS idx_artwork_artist ON artwork(artist_id);
CREATE INDEX IF NOT EXISTS idx_exhibition_gallery ON exhibition(gallery_id);
CREATE INDEX IF NOT EXISTS idx_exhibition_curator ON exhibition(curator_id);
CREATE INDEX IF NOT EXISTS idx_artist_gallery_gallery ON artist_gallery(gallery_id);
CREATE INDEX IF NOT EXISTS idx_exhibition_artwork_artwork ON exhibition_artwork(artwork_id);
CREATE INDEX IF NOT EXISTS idx_auction_gallery ON auction(gallery_id);
CREATE INDEX IF NOT EXISTS idx_auction_lot_artwork ON auction_lot(artwork_id);
CREATE INDEX IF NOT EXISTS idx_bid_lot_amount ON bid(lot_id,bid_amount DESC);
CREATE INDEX IF NOT EXISTS idx_bid_bidder ON bid(bidder_id);
CREATE INDEX IF NOT EXISTS idx_sale_collector ON sale(collector_id);
CREATE INDEX IF NOT EXISTS idx_appraisal_artwork_date ON appraisal(artwork_id,appraisal_date DESC);
CREATE INDEX IF NOT EXISTS idx_appraisal_expert ON appraisal(expert_id);
CREATE INDEX IF NOT EXISTS idx_authentication_artwork_date ON authentication(artwork_id,authentication_date DESC);
CREATE INDEX IF NOT EXISTS idx_authentication_expert ON authentication(expert_id);
