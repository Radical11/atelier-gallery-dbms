-- Installed after the baseline historical seed. These guard all future writes.
CREATE OR REPLACE TRIGGER bid_immutable
BEFORE UPDATE OR DELETE ON bid
BEGIN
  RAISE_APPLICATION_ERROR(-20001,'Accepted bid history is immutable');
END;
/
CREATE OR REPLACE TRIGGER sale_immutable
BEFORE DELETE OR UPDATE OF bid_id,collector_id,sale_price,sale_date ON sale
BEGIN
  RAISE_APPLICATION_ERROR(-20002,'Finalized sale history is immutable');
END;
/
-- A compound trigger avoids selecting the mutating BID table from a row trigger.
CREATE OR REPLACE TRIGGER validate_bid
FOR INSERT ON bid COMPOUND TRIGGER
  TYPE ids IS TABLE OF NUMBER INDEX BY PLS_INTEGER;
  bid_ids ids; n PLS_INTEGER := 0;
  BEFORE EACH ROW IS
    lot_status VARCHAR2(20); auction_status VARCHAR2(20); start_price NUMBER;
  BEGIN
    SELECT l.status,a.status,l.starting_price INTO lot_status,auction_status,start_price
    FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id
    WHERE l.lot_id=:NEW.lot_id FOR UPDATE OF l.status;
    IF lot_status <> 'open' OR auction_status <> 'open' OR :NEW.bid_amount < start_price THEN
      RAISE_APPLICATION_ERROR(-20003,'Lot must be open and bid must meet starting price');
    END IF;
    n:=n+1; bid_ids(n):=:NEW.bid_id;
  END BEFORE EACH ROW;
  AFTER STATEMENT IS
    invalid_count NUMBER;
  BEGIN
    FOR i IN 1..n LOOP
      SELECT COUNT(*) INTO invalid_count FROM bid b
      WHERE b.bid_id=bid_ids(i) AND EXISTS
        (SELECT 1 FROM bid other WHERE other.lot_id=b.lot_id AND other.bid_id<>b.bid_id AND other.bid_amount>=b.bid_amount);
      IF invalid_count>0 THEN RAISE_APPLICATION_ERROR(-20004,'Bid must exceed the current highest bid'); END IF;
    END LOOP;
  END AFTER STATEMENT;
END;
/
CREATE OR REPLACE TRIGGER validate_sale
FOR INSERT ON sale COMPOUND TRIGGER
  TYPE ids IS TABLE OF NUMBER INDEX BY PLS_INTEGER;
  sale_ids ids; n PLS_INTEGER := 0;
  BEFORE EACH ROW IS
    locked_id NUMBER;
  BEGIN
    SELECT l.lot_id INTO locked_id FROM auction_lot l JOIN bid b ON b.lot_id=l.lot_id
    WHERE b.bid_id=:NEW.bid_id FOR UPDATE OF l.status;
    n:=n+1; sale_ids(n):=:NEW.sale_id;
  END BEFORE EACH ROW;
  AFTER STATEMENT IS
    valid_count NUMBER;
  BEGIN
    FOR i IN 1..n LOOP
      SELECT COUNT(*) INTO valid_count FROM sale s JOIN bid b ON b.bid_id=s.bid_id
      JOIN auction_lot l ON l.lot_id=b.lot_id JOIN collector c ON c.collector_id=s.collector_id
      WHERE s.sale_id=sale_ids(i) AND l.status='open' AND c.bidder_id=b.bidder_id
        AND s.sale_price=b.bid_amount AND b.bid_amount>=l.reserve_price
        AND NOT EXISTS (SELECT 1 FROM bid other WHERE other.lot_id=b.lot_id AND other.bid_amount>b.bid_amount)
        AND NOT EXISTS (SELECT 1 FROM sale other JOIN bid ob ON ob.bid_id=other.bid_id
                        WHERE ob.lot_id=b.lot_id AND other.sale_id<>s.sale_id);
      IF valid_count<>1 THEN RAISE_APPLICATION_ERROR(-20005,'Sale must match the winning bid, reserve and collector'); END IF;
    END LOOP;
  END AFTER STATEMENT;
END;
/
CREATE OR REPLACE TRIGGER lot_insert_guard
BEFORE INSERT ON auction_lot FOR EACH ROW
DECLARE auction_status VARCHAR2(20);
BEGIN
  SELECT status INTO auction_status FROM auction WHERE auction_id=:NEW.auction_id;
  IF :NEW.status<>'draft' OR auction_status<>'draft' THEN
    RAISE_APPLICATION_ERROR(-20006,'New lots require a draft auction');
  END IF;
END;
/
CREATE OR REPLACE TRIGGER lot_update_guard
BEFORE UPDATE OR DELETE ON auction_lot FOR EACH ROW
DECLARE auction_status VARCHAR2(20); artwork_status VARCHAR2(20); sales_count NUMBER;
BEGIN
  IF :OLD.status IN ('sold','unsold') THEN RAISE_APPLICATION_ERROR(-20007,'Closed lots are immutable'); END IF;
  IF DELETING THEN
    IF :OLD.status='open' THEN RAISE_APPLICATION_ERROR(-20008,'Open lots cannot be deleted'); END IF;
  ELSE
    IF :OLD.status='open' AND (:OLD.auction_id<>:NEW.auction_id OR :OLD.artwork_id<>:NEW.artwork_id
       OR :OLD.lot_number<>:NEW.lot_number OR :OLD.starting_price<>:NEW.starting_price OR :OLD.reserve_price<>:NEW.reserve_price) THEN
      RAISE_APPLICATION_ERROR(-20009,'Open lot details are immutable');
    END IF;
    IF :OLD.status<>:NEW.status THEN
      IF :OLD.status='draft' AND :NEW.status='open' THEN
        SELECT a.status,w.status INTO auction_status,artwork_status FROM auction a CROSS JOIN artwork w
        WHERE a.auction_id=:NEW.auction_id AND w.artwork_id=:NEW.artwork_id;
        IF auction_status<>'open' OR artwork_status<>'available' THEN
          RAISE_APPLICATION_ERROR(-20010,'Only available draft lots can open');
        END IF;
      ELSIF :OLD.status='open' AND :NEW.status IN ('sold','unsold') THEN
        SELECT COUNT(*) INTO sales_count FROM sale s JOIN bid b ON b.bid_id=s.bid_id WHERE b.lot_id=:OLD.lot_id;
        IF (:NEW.status='sold' AND sales_count<>1) OR (:NEW.status='unsold' AND sales_count<>0) THEN
          RAISE_APPLICATION_ERROR(-20011,'Lot status must match its sale');
        END IF;
      ELSE RAISE_APPLICATION_ERROR(-20012,'Invalid lot status transition');
      END IF;
    END IF;
  END IF;
END;
/
CREATE OR REPLACE TRIGGER auction_update_guard
BEFORE UPDATE OF status ON auction FOR EACH ROW
DECLARE unfinished NUMBER;
BEGIN
  IF :OLD.status<>:NEW.status THEN
    IF NOT (:OLD.status='draft' AND :NEW.status='open' OR :OLD.status='open' AND :NEW.status='closed') THEN
      RAISE_APPLICATION_ERROR(-20013,'Invalid auction status transition');
    END IF;
    IF :NEW.status='closed' THEN
      SELECT COUNT(*) INTO unfinished FROM auction_lot WHERE auction_id=:OLD.auction_id AND status IN ('draft','open');
      IF unfinished>0 THEN RAISE_APPLICATION_ERROR(-20014,'Close all lots first'); END IF;
    END IF;
  END IF;
END;
/
