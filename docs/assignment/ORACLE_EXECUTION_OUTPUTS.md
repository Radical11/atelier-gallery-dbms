# Atelier — Oracle SQL execution evidence

Member outputs use the current simplified queries and real names. Group DDL/TCL and workflow outputs are retained from their separately verified execution session. All results below were actually executed in Oracle.

## Group · DDL demonstration

```sql
CREATE TABLE LAB_DDL_100066 (example_id NUMBER PRIMARY KEY,note VARCHAR2(100));
ALTER TABLE LAB_DDL_100066 ADD created_on DATE DEFAULT SYSDATE;
CREATE INDEX LAB_DDL_100066_IX ON LAB_DDL_100066(note);
SELECT column_name,data_type FROM user_tab_columns WHERE table_name='LAB_DDL_100066' ORDER BY column_id;
DROP TABLE LAB_DDL_100066 PURGE;
```

```json
{
  "title": "DDL demonstration",
  "kind": "DDL",
  "presenter": "Group",
  "sql": "CREATE TABLE LAB_DDL_100066 (example_id NUMBER PRIMARY KEY,note VARCHAR2(100));\nALTER TABLE LAB_DDL_100066 ADD created_on DATE DEFAULT SYSDATE;\nCREATE INDEX LAB_DDL_100066_IX ON LAB_DDL_100066(note);\nSELECT column_name,data_type FROM user_tab_columns WHERE table_name='LAB_DDL_100066' ORDER BY column_id;\nDROP TABLE LAB_DDL_100066 PURGE",
  "binds": {},
  "result": {
    "columns": [
      "column_name",
      "data_type"
    ],
    "rows": [
      {
        "column_name": "EXAMPLE_ID",
        "data_type": "NUMBER"
      },
      {
        "column_name": "NOTE",
        "data_type": "VARCHAR2"
      },
      {
        "column_name": "CREATED_ON",
        "data_type": "DATE"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "column_name",
        "data_type"
      ],
      "rows": [
        {
          "column_name": "EXAMPLE_ID",
          "data_type": "NUMBER"
        },
        {
          "column_name": "NOTE",
          "data_type": "VARCHAR2"
        },
        {
          "column_name": "CREATED_ON",
          "data_type": "DATE"
        }
      ],
      "truncated": false
    }
  ],
  "before": null,
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "supplement",
  "query_id": "ddl"
}
```

## Group · TCL demonstration

```sql
INSERT INTO curator(curator_id,name) VALUES(:id,'TCL demonstration');
COMMIT;
SAVEPOINT before_change;
UPDATE curator SET name='Temporary value' WHERE curator_id=:id;
SELECT curator_id,name FROM curator WHERE curator_id=:id;
ROLLBACK TO before_change;
SELECT curator_id,name FROM curator WHERE curator_id=:id;
DELETE FROM curator WHERE curator_id=:id;
ROLLBACK;
SELECT curator_id,name FROM curator WHERE curator_id=:id;
DELETE FROM curator WHERE curator_id=:id;
COMMIT;
```

```json
{
  "title": "TCL demonstration",
  "kind": "TCL",
  "presenter": "Group",
  "sql": "INSERT INTO curator(curator_id,name) VALUES(:id,'TCL demonstration');\nCOMMIT;\nSAVEPOINT before_change;\nUPDATE curator SET name='Temporary value' WHERE curator_id=:id;\nSELECT curator_id,name FROM curator WHERE curator_id=:id;\nROLLBACK TO before_change;\nSELECT curator_id,name FROM curator WHERE curator_id=:id;\nDELETE FROM curator WHERE curator_id=:id;\nROLLBACK;\nSELECT curator_id,name FROM curator WHERE curator_id=:id;\nDELETE FROM curator WHERE curator_id=:id;\nCOMMIT",
  "binds": {},
  "result": {
    "columns": [
      "curator_id",
      "name"
    ],
    "rows": [
      {
        "curator_id": 100068,
        "name": "TCL demonstration"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "curator_id",
        "name"
      ],
      "rows": [
        {
          "curator_id": 100068,
          "name": "Temporary value"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "curator_id",
        "name"
      ],
      "rows": [
        {
          "curator_id": 100068,
          "name": "TCL demonstration"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "curator_id",
        "name"
      ],
      "rows": [
        {
          "curator_id": 100068,
          "name": "TCL demonstration"
        }
      ],
      "truncated": false
    }
  ],
  "before": null,
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "supplement",
  "query_id": "tcl"
}
```

## Group · UNION: people who participate in the art system

```sql
SELECT name FROM artist UNION SELECT name FROM art_expert ORDER BY name;
```

```json
{
  "title": "UNION: people who participate in the art system",
  "kind": "SET-UNION",
  "presenter": "Group",
  "sql": "SELECT name FROM artist UNION SELECT name FROM art_expert ORDER BY name",
  "binds": {},
  "result": {
    "columns": [
      "name"
    ],
    "rows": [
      {
        "name": "Amara Sen"
      },
      {
        "name": "Daniel Roy"
      },
      {
        "name": "Dr. Anika Desai"
      },
      {
        "name": "Isabelle Laurent"
      },
      {
        "name": "Kavita Rao"
      },
      {
        "name": "Leila Haddad"
      },
      {
        "name": "Mateo Alvarez"
      },
      {
        "name": "Noah Kim"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "name"
      ],
      "rows": [
        {
          "name": "Amara Sen"
        },
        {
          "name": "Daniel Roy"
        },
        {
          "name": "Dr. Anika Desai"
        },
        {
          "name": "Isabelle Laurent"
        },
        {
          "name": "Kavita Rao"
        },
        {
          "name": "Leila Haddad"
        },
        {
          "name": "Mateo Alvarez"
        },
        {
          "name": "Noah Kim"
        }
      ],
      "truncated": false
    }
  ],
  "before": null,
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "supplement",
  "query_id": "set-union"
}
```

## Group · INTERSECT: artworks with both assessments

```sql
SELECT artwork_id FROM appraisal INTERSECT SELECT artwork_id FROM authentication;
```

```json
{
  "title": "INTERSECT: artworks with both assessments",
  "kind": "SET-INTERSECT",
  "presenter": "Group",
  "sql": "SELECT artwork_id FROM appraisal INTERSECT SELECT artwork_id FROM authentication",
  "binds": {},
  "result": {
    "columns": [
      "artwork_id"
    ],
    "rows": [
      {
        "artwork_id": 1
      },
      {
        "artwork_id": 4
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id"
      ],
      "rows": [
        {
          "artwork_id": 1
        },
        {
          "artwork_id": 4
        }
      ],
      "truncated": false
    }
  ],
  "before": null,
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "supplement",
  "query_id": "set-intersect"
}
```

## Group · MINUS: artworks without authentication

```sql
SELECT artwork_id FROM artwork MINUS SELECT artwork_id FROM authentication;
```

```json
{
  "title": "MINUS: artworks without authentication",
  "kind": "SET-MINUS",
  "presenter": "Group",
  "sql": "SELECT artwork_id FROM artwork MINUS SELECT artwork_id FROM authentication",
  "binds": {},
  "result": {
    "columns": [
      "artwork_id"
    ],
    "rows": [
      {
        "artwork_id": 2
      },
      {
        "artwork_id": 3
      },
      {
        "artwork_id": 5
      },
      {
        "artwork_id": 6
      },
      {
        "artwork_id": 7
      },
      {
        "artwork_id": 8
      },
      {
        "artwork_id": 9
      },
      {
        "artwork_id": 10
      },
      {
        "artwork_id": 11
      },
      {
        "artwork_id": 12
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id"
      ],
      "rows": [
        {
          "artwork_id": 2
        },
        {
          "artwork_id": 3
        },
        {
          "artwork_id": 5
        },
        {
          "artwork_id": 6
        },
        {
          "artwork_id": 7
        },
        {
          "artwork_id": 8
        },
        {
          "artwork_id": 9
        },
        {
          "artwork_id": 10
        },
        {
          "artwork_id": 11
        },
        {
          "artwork_id": 12
        }
      ],
      "truncated": false
    }
  ],
  "before": null,
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "supplement",
  "query_id": "set-minus"
}
```

## Group · View: completed gallery revenue

```sql
SELECT gallery_id,name,paid_sales,revenue_inr FROM gallery_revenue ORDER BY gallery_id;
```

```json
{
  "title": "View: completed gallery revenue",
  "kind": "VIEW",
  "presenter": "Group",
  "sql": "SELECT gallery_id,name,paid_sales,revenue_inr FROM gallery_revenue ORDER BY gallery_id",
  "binds": {},
  "result": {
    "columns": [
      "gallery_id",
      "name",
      "paid_sales",
      "revenue_inr"
    ],
    "rows": [
      {
        "gallery_id": 1,
        "name": "Atelier Mumbai",
        "paid_sales": 1,
        "revenue_inr": 55000
      },
      {
        "gallery_id": 2,
        "name": "Atelier Delhi",
        "paid_sales": 0,
        "revenue_inr": 0
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "gallery_id",
        "name",
        "paid_sales",
        "revenue_inr"
      ],
      "rows": [
        {
          "gallery_id": 1,
          "name": "Atelier Mumbai",
          "paid_sales": 1,
          "revenue_inr": 55000
        },
        {
          "gallery_id": 2,
          "name": "Atelier Delhi",
          "paid_sales": 0,
          "revenue_inr": 0
        }
      ],
      "truncated": false
    }
  ],
  "before": null,
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "supplement",
  "query_id": "view"
}
```

## Group · ALL: appraisals at least as large as every appraisal

```sql
SELECT appraisal_id,estimated_value/100 AS estimate_inr FROM appraisal WHERE estimated_value >= ALL (SELECT estimated_value FROM appraisal);
```

```json
{
  "title": "ALL: appraisals at least as large as every appraisal",
  "kind": "ANY-ALL",
  "presenter": "Group",
  "sql": "SELECT appraisal_id,estimated_value/100 AS estimate_inr FROM appraisal WHERE estimated_value >= ALL (SELECT estimated_value FROM appraisal)",
  "binds": {},
  "result": {
    "columns": [
      "appraisal_id",
      "estimate_inr"
    ],
    "rows": [
      {
        "appraisal_id": 2,
        "estimate_inr": 80000
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "appraisal_id",
        "estimate_inr"
      ],
      "rows": [
        {
          "appraisal_id": 2,
          "estimate_inr": 80000
        }
      ],
      "truncated": false
    }
  ],
  "before": null,
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "supplement",
  "query_id": "any-all"
}
```

## Group · Create an artwork

```sql
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
INSERT INTO artwork(artwork_id,artist_id,title,year_created,medium,image_path) VALUES(:b0,1,:b1,2026,'Oil on canvas','images/artwork-01.webp');
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
```

```json
{
  "title": "Create an artwork",
  "kind": "WORKFLOW",
  "presenter": "Group",
  "flow": {
    "artwork_id": 100075
  },
  "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nINSERT INTO artwork(artwork_id,artist_id,title,year_created,medium,image_path) VALUES(:b0,1,:b1,2026,'Oil on canvas','images/artwork-01.webp');\nSELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
  "binds": {},
  "executed": [
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "INSERT INTO artwork(artwork_id,artist_id,title,year_created,medium,image_path) VALUES(:b0,1,:b1,2026,'Oil on canvas','images/artwork-01.webp')",
      "binds": {
        "b0": 100075,
        "b1": "Presentation Study 100075"
      }
    },
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    }
  ],
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "available"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id",
        "title",
        "status"
      ],
      "rows": [
        {
          "artwork_id": 100075,
          "title": "Presentation Study 100075",
          "status": "available"
        }
      ],
      "truncated": false
    }
  ],
  "before": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "workflow",
  "query_id": "step1"
}
```

## Group · Assign it to an exhibition

```sql
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
INSERT INTO exhibition_artwork(exhibition_id,artwork_id,display_position) VALUES(1,:b0,'Presentation wall');
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
```

```json
{
  "title": "Assign it to an exhibition",
  "kind": "WORKFLOW",
  "presenter": "Group",
  "flow": {
    "artwork_id": 100075
  },
  "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nINSERT INTO exhibition_artwork(exhibition_id,artwork_id,display_position) VALUES(1,:b0,'Presentation wall');\nSELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
  "binds": {},
  "executed": [
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "INSERT INTO exhibition_artwork(exhibition_id,artwork_id,display_position) VALUES(1,:b0,'Presentation wall')",
      "binds": {
        "b0": 100075
      }
    },
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    }
  ],
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "available"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id",
        "title",
        "status"
      ],
      "rows": [
        {
          "artwork_id": 100075,
          "title": "Presentation Study 100075",
          "status": "available"
        }
      ],
      "truncated": false
    }
  ],
  "before": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "available"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "workflow",
  "query_id": "step2"
}
```

## Group · Record expert assessments

```sql
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT lab_id_seq.NEXTVAL FROM dual;
INSERT INTO appraisal (appraisal_id,artwork_id,expert_id,appraisal_date,estimated_value,notes) VALUES (:b0,:b1,1,TRUNC(SYSDATE),8000000,'Presentation assessment');
SELECT lab_id_seq.NEXTVAL FROM dual;
INSERT INTO authentication (authentication_id,artwork_id,expert_id,certificate_no,authentication_date,result,notes) VALUES (:b0,:b1,1,:b2,TRUNC(SYSDATE),'Authentic','Presentation certificate');
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
```

```json
{
  "title": "Record expert assessments",
  "kind": "WORKFLOW",
  "presenter": "Group",
  "flow": {
    "artwork_id": 100075
  },
  "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT lab_id_seq.NEXTVAL FROM dual;\nINSERT INTO appraisal (appraisal_id,artwork_id,expert_id,appraisal_date,estimated_value,notes) VALUES (:b0,:b1,1,TRUNC(SYSDATE),8000000,'Presentation assessment');\nSELECT lab_id_seq.NEXTVAL FROM dual;\nINSERT INTO authentication (authentication_id,artwork_id,expert_id,certificate_no,authentication_date,result,notes) VALUES (:b0,:b1,1,:b2,TRUNC(SYSDATE),'Authentic','Presentation certificate');\nSELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
  "binds": {},
  "executed": [
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT lab_id_seq.NEXTVAL FROM dual",
      "binds": {}
    },
    {
      "sql": "INSERT INTO appraisal (appraisal_id,artwork_id,expert_id,appraisal_date,estimated_value,notes) VALUES (:b0,:b1,1,TRUNC(SYSDATE),8000000,'Presentation assessment')",
      "binds": {
        "b0": 100078,
        "b1": 100075
      }
    },
    {
      "sql": "SELECT lab_id_seq.NEXTVAL FROM dual",
      "binds": {}
    },
    {
      "sql": "INSERT INTO authentication (authentication_id,artwork_id,expert_id,certificate_no,authentication_date,result,notes) VALUES (:b0,:b1,1,:b2,TRUNC(SYSDATE),'Authentic','Presentation certificate')",
      "binds": {
        "b0": 100079,
        "b1": 100075,
        "b2": "DEMO-100075"
      }
    },
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    }
  ],
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "available"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id",
        "title",
        "status"
      ],
      "rows": [
        {
          "artwork_id": 100075,
          "title": "Presentation Study 100075",
          "status": "available"
        }
      ],
      "truncated": false
    }
  ],
  "before": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "available"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "workflow",
  "query_id": "step3"
}
```

## Group · Create and open an auction

```sql
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT lab_id_seq.NEXTVAL FROM dual;
INSERT INTO auction (auction_id,gallery_id,title,"DATE",venue) VALUES (:b0,1,:b1,TRUNC(SYSDATE),'Atelier Mumbai');
SELECT lab_id_seq.NEXTVAL FROM dual;
INSERT INTO auction_lot (lot_id,auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES (:b0,:b1,:b2,1,5000000,6000000);
SELECT status FROM auction WHERE auction_id=:b0 FOR UPDATE;
SELECT l.lot_id, l.artwork_id, l.status, w.status AS artwork_status FROM auction_lot l JOIN artwork w ON w.artwork_id=l.artwork_id WHERE l.auction_id=:b0;
SELECT status FROM artwork WHERE artwork_id=:b0 FOR UPDATE;
SELECT 1 FROM auction_lot WHERE artwork_id=:b0 AND status='open';
UPDATE auction SET status='open' WHERE auction_id=:b0;
UPDATE auction_lot SET status='open' WHERE lot_id=:b0;
UPDATE artwork SET status='at_auction' WHERE artwork_id=:b0;
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id;
```

```json
{
  "title": "Create and open an auction",
  "kind": "WORKFLOW",
  "presenter": "Group",
  "flow": {
    "artwork_id": 100075,
    "auction_id": 100081,
    "lot_id": 100082
  },
  "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT lab_id_seq.NEXTVAL FROM dual;\nINSERT INTO auction (auction_id,gallery_id,title,\"DATE\",venue) VALUES (:b0,1,:b1,TRUNC(SYSDATE),'Atelier Mumbai');\nSELECT lab_id_seq.NEXTVAL FROM dual;\nINSERT INTO auction_lot (lot_id,auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES (:b0,:b1,:b2,1,5000000,6000000);\nSELECT status FROM auction WHERE auction_id=:b0 FOR UPDATE;\nSELECT l.lot_id, l.artwork_id, l.status, w.status AS artwork_status FROM auction_lot l JOIN artwork w ON w.artwork_id=l.artwork_id WHERE l.auction_id=:b0;\nSELECT status FROM artwork WHERE artwork_id=:b0 FOR UPDATE;\nSELECT 1 FROM auction_lot WHERE artwork_id=:b0 AND status='open';\nUPDATE auction SET status='open' WHERE auction_id=:b0;\nUPDATE auction_lot SET status='open' WHERE lot_id=:b0;\nUPDATE artwork SET status='at_auction' WHERE artwork_id=:b0;\nSELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id",
  "binds": {},
  "executed": [
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT lab_id_seq.NEXTVAL FROM dual",
      "binds": {}
    },
    {
      "sql": "INSERT INTO auction (auction_id,gallery_id,title,\"DATE\",venue) VALUES (:b0,1,:b1,TRUNC(SYSDATE),'Atelier Mumbai')",
      "binds": {
        "b0": 100081,
        "b1": "Presentation Auction 100075"
      }
    },
    {
      "sql": "SELECT lab_id_seq.NEXTVAL FROM dual",
      "binds": {}
    },
    {
      "sql": "INSERT INTO auction_lot (lot_id,auction_id,artwork_id,lot_number,starting_price,reserve_price) VALUES (:b0,:b1,:b2,1,5000000,6000000)",
      "binds": {
        "b0": 100082,
        "b1": 100081,
        "b2": 100075
      }
    },
    {
      "sql": "SELECT status FROM auction WHERE auction_id=:b0 FOR UPDATE",
      "binds": {
        "b0": 100081
      }
    },
    {
      "sql": "SELECT l.lot_id, l.artwork_id, l.status, w.status AS artwork_status FROM auction_lot l JOIN artwork w ON w.artwork_id=l.artwork_id WHERE l.auction_id=:b0",
      "binds": {
        "b0": 100081
      }
    },
    {
      "sql": "SELECT status FROM artwork WHERE artwork_id=:b0 FOR UPDATE",
      "binds": {
        "b0": 100075
      }
    },
    {
      "sql": "SELECT 1 FROM auction_lot WHERE artwork_id=:b0 AND status='open'",
      "binds": {
        "b0": 100075
      }
    },
    {
      "sql": "UPDATE auction SET status='open' WHERE auction_id=:b0",
      "binds": {
        "b0": 100081
      }
    },
    {
      "sql": "UPDATE auction_lot SET status='open' WHERE lot_id=:b0",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "UPDATE artwork SET status='at_auction' WHERE artwork_id=:b0",
      "binds": {
        "b0": 100075
      }
    },
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id",
      "binds": {
        "id": 100082
      }
    }
  ],
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "at_auction"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id",
        "title",
        "status"
      ],
      "rows": [
        {
          "artwork_id": 100075,
          "title": "Presentation Study 100075",
          "status": "at_auction"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "lot_id",
        "status",
        "highest_bid_inr"
      ],
      "rows": [
        {
          "lot_id": 100082,
          "status": "open",
          "highest_bid_inr": null
        }
      ],
      "truncated": false
    }
  ],
  "before": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "available"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "workflow",
  "query_id": "step4"
}
```

## Group · Maya bids ₹65,000

```sql
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT auction_id FROM auction_lot WHERE lot_id=:b0;
SELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE;
SELECT l.status, l.starting_price, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status;
SELECT 1 FROM bidder WHERE bidder_id=:b0;
SELECT MAX(bid_amount) FROM bid WHERE lot_id=:b0;
SELECT lab_id_seq.NEXTVAL FROM dual;
INSERT INTO bid (bid_id,lot_id,bidder_id,bid_amount) VALUES (:b0,:b1,:b2,:b3);
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id;
```

```json
{
  "title": "Maya bids ₹65,000",
  "kind": "WORKFLOW",
  "presenter": "Group",
  "flow": {
    "artwork_id": 100075,
    "auction_id": 100081,
    "lot_id": 100082,
    "bid_id": 100084
  },
  "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT auction_id FROM auction_lot WHERE lot_id=:b0;\nSELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE;\nSELECT l.status, l.starting_price, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status;\nSELECT 1 FROM bidder WHERE bidder_id=:b0;\nSELECT MAX(bid_amount) FROM bid WHERE lot_id=:b0;\nSELECT lab_id_seq.NEXTVAL FROM dual;\nINSERT INTO bid (bid_id,lot_id,bidder_id,bid_amount) VALUES (:b0,:b1,:b2,:b3);\nSELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id",
  "binds": {},
  "executed": [
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT auction_id FROM auction_lot WHERE lot_id=:b0",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE",
      "binds": {
        "b0": 100081
      }
    },
    {
      "sql": "SELECT l.status, l.starting_price, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT 1 FROM bidder WHERE bidder_id=:b0",
      "binds": {
        "b0": 1
      }
    },
    {
      "sql": "SELECT MAX(bid_amount) FROM bid WHERE lot_id=:b0",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT lab_id_seq.NEXTVAL FROM dual",
      "binds": {}
    },
    {
      "sql": "INSERT INTO bid (bid_id,lot_id,bidder_id,bid_amount) VALUES (:b0,:b1,:b2,:b3)",
      "binds": {
        "b0": 100084,
        "b1": 100082,
        "b2": 1,
        "b3": 6500000
      }
    },
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id",
      "binds": {
        "id": 100082
      }
    }
  ],
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "at_auction"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id",
        "title",
        "status"
      ],
      "rows": [
        {
          "artwork_id": 100075,
          "title": "Presentation Study 100075",
          "status": "at_auction"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "lot_id",
        "status",
        "highest_bid_inr"
      ],
      "rows": [
        {
          "lot_id": 100082,
          "status": "open",
          "highest_bid_inr": 65000
        }
      ],
      "truncated": false
    }
  ],
  "before": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "at_auction"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "workflow",
  "query_id": "step5"
}
```

## Group · Sara bids ₹70,000

```sql
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT auction_id FROM auction_lot WHERE lot_id=:b0;
SELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE;
SELECT l.status, l.starting_price, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status;
SELECT 1 FROM bidder WHERE bidder_id=:b0;
SELECT MAX(bid_amount) FROM bid WHERE lot_id=:b0;
SELECT lab_id_seq.NEXTVAL FROM dual;
INSERT INTO bid (bid_id,lot_id,bidder_id,bid_amount) VALUES (:b0,:b1,:b2,:b3);
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id;
```

```json
{
  "title": "Sara bids ₹70,000",
  "kind": "WORKFLOW",
  "presenter": "Group",
  "flow": {
    "artwork_id": 100075,
    "auction_id": 100081,
    "lot_id": 100082,
    "bid_id": 100086
  },
  "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT auction_id FROM auction_lot WHERE lot_id=:b0;\nSELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE;\nSELECT l.status, l.starting_price, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status;\nSELECT 1 FROM bidder WHERE bidder_id=:b0;\nSELECT MAX(bid_amount) FROM bid WHERE lot_id=:b0;\nSELECT lab_id_seq.NEXTVAL FROM dual;\nINSERT INTO bid (bid_id,lot_id,bidder_id,bid_amount) VALUES (:b0,:b1,:b2,:b3);\nSELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id",
  "binds": {},
  "executed": [
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT auction_id FROM auction_lot WHERE lot_id=:b0",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE",
      "binds": {
        "b0": 100081
      }
    },
    {
      "sql": "SELECT l.status, l.starting_price, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT 1 FROM bidder WHERE bidder_id=:b0",
      "binds": {
        "b0": 3
      }
    },
    {
      "sql": "SELECT MAX(bid_amount) FROM bid WHERE lot_id=:b0",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT lab_id_seq.NEXTVAL FROM dual",
      "binds": {}
    },
    {
      "sql": "INSERT INTO bid (bid_id,lot_id,bidder_id,bid_amount) VALUES (:b0,:b1,:b2,:b3)",
      "binds": {
        "b0": 100086,
        "b1": 100082,
        "b2": 3,
        "b3": 7000000
      }
    },
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id",
      "binds": {
        "id": 100082
      }
    }
  ],
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "at_auction"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id",
        "title",
        "status"
      ],
      "rows": [
        {
          "artwork_id": 100075,
          "title": "Presentation Study 100075",
          "status": "at_auction"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "lot_id",
        "status",
        "highest_bid_inr"
      ],
      "rows": [
        {
          "lot_id": 100082,
          "status": "open",
          "highest_bid_inr": 70000
        }
      ],
      "truncated": false
    }
  ],
  "before": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "at_auction"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "workflow",
  "query_id": "step6"
}
```

## Group · Close the lot and record the sale

```sql
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT auction_id FROM auction_lot WHERE lot_id=:b0;
SELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE;
SELECT l.*, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status;
SELECT * FROM (SELECT * FROM bid WHERE lot_id=:b0 ORDER BY bid_amount DESC, bid_id DESC) WHERE ROWNUM=1;
SELECT * FROM bidder WHERE bidder_id=:b0 FOR UPDATE;
SELECT collector_id FROM collector WHERE bidder_id=:b0;
SELECT lab_id_seq.NEXTVAL FROM dual;
INSERT INTO collector (collector_id,bidder_id,name,email,phone,address) VALUES (:b0,:b1,:b2,:b3,:b4,:b5);
SELECT collector_id FROM collector WHERE bidder_id=:b0;
SELECT lab_id_seq.NEXTVAL FROM dual;
INSERT INTO sale (sale_id,bid_id,collector_id,sale_price,sale_date,payment_status) VALUES (:b0,:b1,:b2,:b3,TRUNC(SYSDATE),'pending');
UPDATE auction_lot SET status=:b0 WHERE lot_id=:b1;
UPDATE artwork SET status=:b0 WHERE artwork_id=:b1;
SELECT 1 FROM auction_lot WHERE auction_id=:b0 AND status IN ('open','draft');
UPDATE auction SET status='closed' WHERE auction_id=:b0;
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id;
SELECT sale_id,sale_price/100 AS sale_inr,payment_status FROM sale WHERE sale_id=:id;
SELECT * FROM gallery_revenue ORDER BY gallery_id;
```

```json
{
  "title": "Close the lot and record the sale",
  "kind": "WORKFLOW",
  "presenter": "Group",
  "flow": {
    "artwork_id": 100075,
    "auction_id": 100081,
    "lot_id": 100082,
    "bid_id": 100086,
    "sale_id": 100089
  },
  "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT auction_id FROM auction_lot WHERE lot_id=:b0;\nSELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE;\nSELECT l.*, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status;\nSELECT * FROM (SELECT * FROM bid WHERE lot_id=:b0 ORDER BY bid_amount DESC, bid_id DESC) WHERE ROWNUM=1;\nSELECT * FROM bidder WHERE bidder_id=:b0 FOR UPDATE;\nSELECT collector_id FROM collector WHERE bidder_id=:b0;\nSELECT lab_id_seq.NEXTVAL FROM dual;\nINSERT INTO collector (collector_id,bidder_id,name,email,phone,address) VALUES (:b0,:b1,:b2,:b3,:b4,:b5);\nSELECT collector_id FROM collector WHERE bidder_id=:b0;\nSELECT lab_id_seq.NEXTVAL FROM dual;\nINSERT INTO sale (sale_id,bid_id,collector_id,sale_price,sale_date,payment_status) VALUES (:b0,:b1,:b2,:b3,TRUNC(SYSDATE),'pending');\nUPDATE auction_lot SET status=:b0 WHERE lot_id=:b1;\nUPDATE artwork SET status=:b0 WHERE artwork_id=:b1;\nSELECT 1 FROM auction_lot WHERE auction_id=:b0 AND status IN ('open','draft');\nUPDATE auction SET status='closed' WHERE auction_id=:b0;\nSELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id;\nSELECT sale_id,sale_price/100 AS sale_inr,payment_status FROM sale WHERE sale_id=:id;\nSELECT * FROM gallery_revenue ORDER BY gallery_id",
  "binds": {},
  "executed": [
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT auction_id FROM auction_lot WHERE lot_id=:b0",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT auction_id FROM auction WHERE auction_id=:b0 FOR UPDATE",
      "binds": {
        "b0": 100081
      }
    },
    {
      "sql": "SELECT l.*, a.status AS auction_status FROM auction_lot l JOIN auction a ON a.auction_id=l.auction_id WHERE l.lot_id=:b0 FOR UPDATE OF l.status",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT * FROM (SELECT * FROM bid WHERE lot_id=:b0 ORDER BY bid_amount DESC, bid_id DESC) WHERE ROWNUM=1",
      "binds": {
        "b0": 100082
      }
    },
    {
      "sql": "SELECT * FROM bidder WHERE bidder_id=:b0 FOR UPDATE",
      "binds": {
        "b0": 3
      }
    },
    {
      "sql": "SELECT collector_id FROM collector WHERE bidder_id=:b0",
      "binds": {
        "b0": 3
      }
    },
    {
      "sql": "SELECT lab_id_seq.NEXTVAL FROM dual",
      "binds": {}
    },
    {
      "sql": "INSERT INTO collector (collector_id,bidder_id,name,email,phone,address) VALUES (:b0,:b1,:b2,:b3,:b4,:b5)",
      "binds": {
        "b0": 100088,
        "b1": 3,
        "b2": "Sara Khan",
        "b3": "sara@atelier.example",
        "b4": "+91 90000 30003",
        "b5": "Pune"
      }
    },
    {
      "sql": "SELECT collector_id FROM collector WHERE bidder_id=:b0",
      "binds": {
        "b0": 3
      }
    },
    {
      "sql": "SELECT lab_id_seq.NEXTVAL FROM dual",
      "binds": {}
    },
    {
      "sql": "INSERT INTO sale (sale_id,bid_id,collector_id,sale_price,sale_date,payment_status) VALUES (:b0,:b1,:b2,:b3,TRUNC(SYSDATE),'pending')",
      "binds": {
        "b0": 100089,
        "b1": 100086,
        "b2": 100088,
        "b3": 7000000
      }
    },
    {
      "sql": "UPDATE auction_lot SET status=:b0 WHERE lot_id=:b1",
      "binds": {
        "b0": "sold",
        "b1": 100082
      }
    },
    {
      "sql": "UPDATE artwork SET status=:b0 WHERE artwork_id=:b1",
      "binds": {
        "b0": "sold",
        "b1": 100075
      }
    },
    {
      "sql": "SELECT 1 FROM auction_lot WHERE auction_id=:b0 AND status IN ('open','draft')",
      "binds": {
        "b0": 100081
      }
    },
    {
      "sql": "UPDATE auction SET status='closed' WHERE auction_id=:b0",
      "binds": {
        "b0": 100081
      }
    },
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id",
      "binds": {
        "id": 100082
      }
    },
    {
      "sql": "SELECT sale_id,sale_price/100 AS sale_inr,payment_status FROM sale WHERE sale_id=:id",
      "binds": {
        "id": 100089
      }
    },
    {
      "sql": "SELECT * FROM gallery_revenue ORDER BY gallery_id",
      "binds": {}
    }
  ],
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "sold"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id",
        "title",
        "status"
      ],
      "rows": [
        {
          "artwork_id": 100075,
          "title": "Presentation Study 100075",
          "status": "sold"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "lot_id",
        "status",
        "highest_bid_inr"
      ],
      "rows": [
        {
          "lot_id": 100082,
          "status": "sold",
          "highest_bid_inr": 70000
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "sale_id",
        "sale_inr",
        "payment_status"
      ],
      "rows": [
        {
          "sale_id": 100089,
          "sale_inr": 70000,
          "payment_status": "pending"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "gallery_id",
        "name",
        "paid_sales",
        "revenue_inr"
      ],
      "rows": [
        {
          "gallery_id": 1,
          "name": "Atelier Mumbai",
          "paid_sales": 1,
          "revenue_inr": 55000
        },
        {
          "gallery_id": 2,
          "name": "Atelier Delhi",
          "paid_sales": 0,
          "revenue_inr": 0
        }
      ],
      "truncated": false
    }
  ],
  "before": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "at_auction"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "workflow",
  "query_id": "step7"
}
```

## Group · Complete payment and show revenue

```sql
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT 1 FROM sale WHERE sale_id=:b0;
UPDATE sale SET payment_status=:b0 WHERE sale_id=:b1;
SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;
SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id;
SELECT sale_id,sale_price/100 AS sale_inr,payment_status FROM sale WHERE sale_id=:id;
SELECT * FROM gallery_revenue ORDER BY gallery_id;
```

```json
{
  "title": "Complete payment and show revenue",
  "kind": "WORKFLOW",
  "presenter": "Group",
  "flow": {
    "artwork_id": 100075,
    "auction_id": 100081,
    "lot_id": 100082,
    "bid_id": 100086,
    "sale_id": 100089
  },
  "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT 1 FROM sale WHERE sale_id=:b0;\nUPDATE sale SET payment_status=:b0 WHERE sale_id=:b1;\nSELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id;\nSELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id;\nSELECT sale_id,sale_price/100 AS sale_inr,payment_status FROM sale WHERE sale_id=:id;\nSELECT * FROM gallery_revenue ORDER BY gallery_id",
  "binds": {},
  "executed": [
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT 1 FROM sale WHERE sale_id=:b0",
      "binds": {
        "b0": 100089
      }
    },
    {
      "sql": "UPDATE sale SET payment_status=:b0 WHERE sale_id=:b1",
      "binds": {
        "b0": "completed",
        "b1": 100089
      }
    },
    {
      "sql": "SELECT artwork_id,title,status FROM artwork WHERE artwork_id=:id",
      "binds": {
        "id": 100075
      }
    },
    {
      "sql": "SELECT lot_id,status,(SELECT MAX(bid_amount)/100 FROM bid b WHERE b.lot_id=l.lot_id) AS highest_bid_inr FROM auction_lot l WHERE lot_id=:id",
      "binds": {
        "id": 100082
      }
    },
    {
      "sql": "SELECT sale_id,sale_price/100 AS sale_inr,payment_status FROM sale WHERE sale_id=:id",
      "binds": {
        "id": 100089
      }
    },
    {
      "sql": "SELECT * FROM gallery_revenue ORDER BY gallery_id",
      "binds": {}
    }
  ],
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "sold"
      }
    ],
    "truncated": false
  },
  "outputs": [
    {
      "columns": [
        "artwork_id",
        "title",
        "status"
      ],
      "rows": [
        {
          "artwork_id": 100075,
          "title": "Presentation Study 100075",
          "status": "sold"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "lot_id",
        "status",
        "highest_bid_inr"
      ],
      "rows": [
        {
          "lot_id": 100082,
          "status": "sold",
          "highest_bid_inr": 70000
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "sale_id",
        "sale_inr",
        "payment_status"
      ],
      "rows": [
        {
          "sale_id": 100089,
          "sale_inr": 70000,
          "payment_status": "completed"
        }
      ],
      "truncated": false
    },
    {
      "columns": [
        "gallery_id",
        "name",
        "paid_sales",
        "revenue_inr"
      ],
      "rows": [
        {
          "gallery_id": 1,
          "name": "Atelier Mumbai",
          "paid_sales": 2,
          "revenue_inr": 125000
        },
        {
          "gallery_id": 2,
          "name": "Atelier Delhi",
          "paid_sales": 0,
          "revenue_inr": 0
        }
      ],
      "truncated": false
    }
  ],
  "before": {
    "columns": [
      "artwork_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "status": "sold"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "workflow",
  "query_id": "step8"
}
```

## Vihaan · Create a demonstration record

```sql
INSERT INTO artwork (artwork_id, artist_id, title)
VALUES (:record_id, 1, :value);
```

```json
{
  "title": "Create a demonstration record",
  "kind": "INSERT",
  "presenter": "Vihaan",
  "sql": "INSERT INTO artwork (artwork_id, artist_id, title)\nVALUES (:record_id, 1, :value)",
  "binds": {
    "record_id": 100129,
    "value": "Study in Light"
  },
  "before": {
    "columns": [
      "artwork_id",
      "artist_id",
      "title",
      "year_created",
      "medium",
      "dimensions",
      "description",
      "status",
      "image_path"
    ],
    "rows": [],
    "truncated": false
  },
  "result": {
    "columns": [
      "artwork_id",
      "artist_id",
      "title",
      "year_created",
      "medium",
      "dimensions",
      "description",
      "status",
      "image_path"
    ],
    "rows": [
      {
        "artwork_id": 100129,
        "artist_id": 1,
        "title": "Study in Light",
        "year_created": null,
        "medium": null,
        "dimensions": null,
        "description": null,
        "status": "available",
        "image_path": null
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "collection",
  "query_id": "insert"
}
```

## Vihaan · Update that record

```sql
UPDATE artwork
SET title = :value
WHERE artwork_id = :record_id;
```

```json
{
  "title": "Update that record",
  "kind": "UPDATE",
  "presenter": "Vihaan",
  "sql": "UPDATE artwork\nSET title = :value\nWHERE artwork_id = :record_id",
  "binds": {
    "record_id": 100129,
    "value": "Study in Light revised"
  },
  "before": {
    "columns": [
      "artwork_id",
      "artist_id",
      "title",
      "year_created",
      "medium",
      "dimensions",
      "description",
      "status",
      "image_path"
    ],
    "rows": [
      {
        "artwork_id": 100129,
        "artist_id": 1,
        "title": "Study in Light",
        "year_created": null,
        "medium": null,
        "dimensions": null,
        "description": null,
        "status": "available",
        "image_path": null
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "artwork_id",
      "artist_id",
      "title",
      "year_created",
      "medium",
      "dimensions",
      "description",
      "status",
      "image_path"
    ],
    "rows": [
      {
        "artwork_id": 100129,
        "artist_id": 1,
        "title": "Study in Light revised",
        "year_created": null,
        "medium": null,
        "dimensions": null,
        "description": null,
        "status": "available",
        "image_path": null
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "collection",
  "query_id": "update"
}
```

## Vihaan · Delete that demonstration record

```sql
DELETE FROM artwork
WHERE artwork_id = :record_id;
```

```json
{
  "title": "Delete that demonstration record",
  "kind": "DELETE",
  "presenter": "Vihaan",
  "sql": "DELETE FROM artwork\nWHERE artwork_id = :record_id",
  "binds": {
    "record_id": 100129
  },
  "before": {
    "columns": [
      "artwork_id",
      "artist_id",
      "title",
      "year_created",
      "medium",
      "dimensions",
      "description",
      "status",
      "image_path"
    ],
    "rows": [
      {
        "artwork_id": 100129,
        "artist_id": 1,
        "title": "Study in Light revised",
        "year_created": null,
        "medium": null,
        "dimensions": null,
        "description": null,
        "status": "available",
        "image_path": null
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "artwork_id",
      "artist_id",
      "title",
      "year_created",
      "medium",
      "dimensions",
      "description",
      "status",
      "image_path"
    ],
    "rows": [],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "collection",
  "query_id": "delete"
}
```

## Vihaan · Search artworks by title

```sql
SELECT artwork_id, title, medium
FROM artwork
WHERE title LIKE :search;
```

```json
{
  "title": "Search artworks by title",
  "kind": "SELECT",
  "presenter": "Vihaan",
  "sql": "SELECT artwork_id, title, medium\nFROM artwork\nWHERE title LIKE :search",
  "binds": {
    "search": "%%"
  },
  "before": null,
  "result": {
    "columns": [
      "artwork_id",
      "title",
      "medium"
    ],
    "rows": [
      {
        "artwork_id": 1,
        "title": "Monsoon Reverie",
        "medium": "Oil on canvas"
      },
      {
        "artwork_id": 2,
        "title": "A Quiet Morning",
        "medium": "Acrylic on canvas"
      },
      {
        "artwork_id": 3,
        "title": "Blue Distance",
        "medium": "Oil on linen"
      },
      {
        "artwork_id": 4,
        "title": "The Golden Hour",
        "medium": "Mixed media"
      },
      {
        "artwork_id": 5,
        "title": "Garden of Echoes",
        "medium": "Acrylic on canvas"
      },
      {
        "artwork_id": 6,
        "title": "Between Tides",
        "medium": "Oil on canvas"
      },
      {
        "artwork_id": 7,
        "title": "Window to the City",
        "medium": "Watercolour"
      },
      {
        "artwork_id": 8,
        "title": "Soft Horizons",
        "medium": "Oil on linen"
      },
      {
        "artwork_id": 9,
        "title": "A Place to Begin",
        "medium": "Mixed media"
      },
      {
        "artwork_id": 10,
        "title": "Wild Geometry",
        "medium": "Acrylic on canvas"
      },
      {
        "artwork_id": 11,
        "title": "Evening Passage",
        "medium": "Oil on canvas"
      },
      {
        "artwork_id": 12,
        "title": "The Light Within",
        "medium": "Watercolour"
      },
      {
        "artwork_id": 100093,
        "title": "Transaction demonstration 100092 / 1",
        "medium": "Oil on canvas"
      },
      {
        "artwork_id": 100075,
        "title": "Presentation Study 100075",
        "medium": "Oil on canvas"
      },
      {
        "artwork_id": 100095,
        "title": "Transaction demonstration 100094 / 2",
        "medium": "Oil on canvas"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "collection",
  "query_id": "select1"
}
```

## Vihaan · Show each artwork and its artist

```sql
SELECT w.title, a.name
FROM artwork w
JOIN artist a ON w.artist_id = a.artist_id;
```

```json
{
  "title": "Show each artwork and its artist",
  "kind": "SELECT",
  "presenter": "Vihaan",
  "sql": "SELECT w.title, a.name\nFROM artwork w\nJOIN artist a ON w.artist_id = a.artist_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "title",
      "name"
    ],
    "rows": [
      {
        "title": "Monsoon Reverie",
        "name": "Amara Sen"
      },
      {
        "title": "A Place to Begin",
        "name": "Amara Sen"
      },
      {
        "title": "Transaction demonstration 100092 / 1",
        "name": "Amara Sen"
      },
      {
        "title": "Presentation Study 100075",
        "name": "Amara Sen"
      },
      {
        "title": "Transaction demonstration 100094 / 2",
        "name": "Amara Sen"
      },
      {
        "title": "A Quiet Morning",
        "name": "Kavita Rao"
      },
      {
        "title": "Window to the City",
        "name": "Kavita Rao"
      },
      {
        "title": "Blue Distance",
        "name": "Isabelle Laurent"
      },
      {
        "title": "Soft Horizons",
        "name": "Isabelle Laurent"
      },
      {
        "title": "The Golden Hour",
        "name": "Noah Kim"
      },
      {
        "title": "The Light Within",
        "name": "Noah Kim"
      },
      {
        "title": "Garden of Echoes",
        "name": "Leila Haddad"
      },
      {
        "title": "Wild Geometry",
        "name": "Leila Haddad"
      },
      {
        "title": "Between Tides",
        "name": "Mateo Alvarez"
      },
      {
        "title": "Evening Passage",
        "name": "Mateo Alvarez"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "collection",
  "query_id": "select2"
}
```

## Vihaan · Count artworks for each artist

```sql
SELECT artist_id, COUNT(*) AS total_artworks
FROM artwork
GROUP BY artist_id;
```

```json
{
  "title": "Count artworks for each artist",
  "kind": "SELECT",
  "presenter": "Vihaan",
  "sql": "SELECT artist_id, COUNT(*) AS total_artworks\nFROM artwork\nGROUP BY artist_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "artist_id",
      "total_artworks"
    ],
    "rows": [
      {
        "artist_id": 1,
        "total_artworks": 5
      },
      {
        "artist_id": 2,
        "total_artworks": 2
      },
      {
        "artist_id": 3,
        "total_artworks": 2
      },
      {
        "artist_id": 4,
        "total_artworks": 2
      },
      {
        "artist_id": 5,
        "total_artworks": 2
      },
      {
        "artist_id": 6,
        "total_artworks": 2
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "collection",
  "query_id": "select3"
}
```

## Vihaan · Find artworks by Indian artists

```sql
SELECT title
FROM artwork
WHERE artist_id IN (
    SELECT artist_id FROM artist WHERE nationality = 'Indian'
);
```

```json
{
  "title": "Find artworks by Indian artists",
  "kind": "SELECT",
  "presenter": "Vihaan",
  "sql": "SELECT title\nFROM artwork\nWHERE artist_id IN (\n    SELECT artist_id FROM artist WHERE nationality = 'Indian'\n)",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "title"
    ],
    "rows": [
      {
        "title": "Monsoon Reverie"
      },
      {
        "title": "A Place to Begin"
      },
      {
        "title": "Transaction demonstration 100092 / 1"
      },
      {
        "title": "Presentation Study 100075"
      },
      {
        "title": "Transaction demonstration 100094 / 2"
      },
      {
        "title": "A Quiet Morning"
      },
      {
        "title": "Window to the City"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "collection",
  "query_id": "select4"
}
```

## Vihaan · Show artwork titles in capital letters

```sql
SELECT UPPER(title) AS title_in_capitals
FROM artwork;
```

```json
{
  "title": "Show artwork titles in capital letters",
  "kind": "SELECT",
  "presenter": "Vihaan",
  "sql": "SELECT UPPER(title) AS title_in_capitals\nFROM artwork",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "title_in_capitals"
    ],
    "rows": [
      {
        "title_in_capitals": "MONSOON REVERIE"
      },
      {
        "title_in_capitals": "A QUIET MORNING"
      },
      {
        "title_in_capitals": "BLUE DISTANCE"
      },
      {
        "title_in_capitals": "THE GOLDEN HOUR"
      },
      {
        "title_in_capitals": "GARDEN OF ECHOES"
      },
      {
        "title_in_capitals": "BETWEEN TIDES"
      },
      {
        "title_in_capitals": "WINDOW TO THE CITY"
      },
      {
        "title_in_capitals": "SOFT HORIZONS"
      },
      {
        "title_in_capitals": "A PLACE TO BEGIN"
      },
      {
        "title_in_capitals": "WILD GEOMETRY"
      },
      {
        "title_in_capitals": "EVENING PASSAGE"
      },
      {
        "title_in_capitals": "THE LIGHT WITHIN"
      },
      {
        "title_in_capitals": "TRANSACTION DEMONSTRATION 100092 / 1"
      },
      {
        "title_in_capitals": "PRESENTATION STUDY 100075"
      },
      {
        "title_in_capitals": "TRANSACTION DEMONSTRATION 100094 / 2"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "collection",
  "query_id": "select5"
}
```

## Kaashvi · Create a demonstration record

```sql
INSERT INTO exhibition
    (exhibition_id, gallery_id, curator_id, title, start_date, end_date)
VALUES (:record_id, 1, 1, :value, DATE '2026-11-01', DATE '2026-12-31');
```

```json
{
  "title": "Create a demonstration record",
  "kind": "INSERT",
  "presenter": "Kaashvi",
  "sql": "INSERT INTO exhibition\n    (exhibition_id, gallery_id, curator_id, title, start_date, end_date)\nVALUES (:record_id, 1, 1, :value, DATE '2026-11-01', DATE '2026-12-31')",
  "binds": {
    "record_id": 100138,
    "value": "Light and Memory"
  },
  "before": {
    "columns": [
      "exhibition_id",
      "gallery_id",
      "curator_id",
      "title",
      "start_date",
      "end_date",
      "theme"
    ],
    "rows": [],
    "truncated": false
  },
  "result": {
    "columns": [
      "exhibition_id",
      "gallery_id",
      "curator_id",
      "title",
      "start_date",
      "end_date",
      "theme"
    ],
    "rows": [
      {
        "exhibition_id": 100138,
        "gallery_id": 1,
        "curator_id": 1,
        "title": "Light and Memory",
        "start_date": "2026-11-01",
        "end_date": "2026-12-31",
        "theme": null
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "exhibitions",
  "query_id": "insert"
}
```

## Kaashvi · Update that record

```sql
UPDATE exhibition
SET title = :value
WHERE exhibition_id = :record_id;
```

```json
{
  "title": "Update that record",
  "kind": "UPDATE",
  "presenter": "Kaashvi",
  "sql": "UPDATE exhibition\nSET title = :value\nWHERE exhibition_id = :record_id",
  "binds": {
    "record_id": 100138,
    "value": "Light and Memory revised"
  },
  "before": {
    "columns": [
      "exhibition_id",
      "gallery_id",
      "curator_id",
      "title",
      "start_date",
      "end_date",
      "theme"
    ],
    "rows": [
      {
        "exhibition_id": 100138,
        "gallery_id": 1,
        "curator_id": 1,
        "title": "Light and Memory",
        "start_date": "2026-11-01",
        "end_date": "2026-12-31",
        "theme": null
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "exhibition_id",
      "gallery_id",
      "curator_id",
      "title",
      "start_date",
      "end_date",
      "theme"
    ],
    "rows": [
      {
        "exhibition_id": 100138,
        "gallery_id": 1,
        "curator_id": 1,
        "title": "Light and Memory revised",
        "start_date": "2026-11-01",
        "end_date": "2026-12-31",
        "theme": null
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "exhibitions",
  "query_id": "update"
}
```

## Kaashvi · Delete that demonstration record

```sql
DELETE FROM exhibition
WHERE exhibition_id = :record_id;
```

```json
{
  "title": "Delete that demonstration record",
  "kind": "DELETE",
  "presenter": "Kaashvi",
  "sql": "DELETE FROM exhibition\nWHERE exhibition_id = :record_id",
  "binds": {
    "record_id": 100138
  },
  "before": {
    "columns": [
      "exhibition_id",
      "gallery_id",
      "curator_id",
      "title",
      "start_date",
      "end_date",
      "theme"
    ],
    "rows": [
      {
        "exhibition_id": 100138,
        "gallery_id": 1,
        "curator_id": 1,
        "title": "Light and Memory revised",
        "start_date": "2026-11-01",
        "end_date": "2026-12-31",
        "theme": null
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "exhibition_id",
      "gallery_id",
      "curator_id",
      "title",
      "start_date",
      "end_date",
      "theme"
    ],
    "rows": [],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "exhibitions",
  "query_id": "delete"
}
```

## Kaashvi · Search exhibitions by title

```sql
SELECT exhibition_id, title, start_date, end_date
FROM exhibition
WHERE title LIKE :search;
```

```json
{
  "title": "Search exhibitions by title",
  "kind": "SELECT",
  "presenter": "Kaashvi",
  "sql": "SELECT exhibition_id, title, start_date, end_date\nFROM exhibition\nWHERE title LIKE :search",
  "binds": {
    "search": "%%"
  },
  "before": null,
  "result": {
    "columns": [
      "exhibition_id",
      "title",
      "start_date",
      "end_date"
    ],
    "rows": [
      {
        "exhibition_id": 100116,
        "title": "Light and Memory",
        "start_date": "2026-11-01",
        "end_date": "2026-12-31"
      },
      {
        "exhibition_id": 1,
        "title": "Colour and Memory",
        "start_date": "2026-10-01",
        "end_date": "2026-12-20"
      },
      {
        "exhibition_id": 2,
        "title": "Quiet Places",
        "start_date": "2026-11-01",
        "end_date": "2027-01-15"
      },
      {
        "exhibition_id": 3,
        "title": "New Perspectives",
        "start_date": "2027-02-01",
        "end_date": "2027-03-31"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "exhibitions",
  "query_id": "select1"
}
```

## Kaashvi · Show each exhibition and its gallery

```sql
SELECT e.title, g.name
FROM exhibition e
JOIN gallery g ON e.gallery_id = g.gallery_id;
```

```json
{
  "title": "Show each exhibition and its gallery",
  "kind": "SELECT",
  "presenter": "Kaashvi",
  "sql": "SELECT e.title, g.name\nFROM exhibition e\nJOIN gallery g ON e.gallery_id = g.gallery_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "title",
      "name"
    ],
    "rows": [
      {
        "title": "Light and Memory",
        "name": "Atelier Mumbai"
      },
      {
        "title": "Colour and Memory",
        "name": "Atelier Mumbai"
      },
      {
        "title": "New Perspectives",
        "name": "Atelier Mumbai"
      },
      {
        "title": "Quiet Places",
        "name": "Atelier Delhi"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "exhibitions",
  "query_id": "select2"
}
```

## Kaashvi · Count exhibitions for each gallery

```sql
SELECT gallery_id, COUNT(*) AS total_exhibitions
FROM exhibition
GROUP BY gallery_id;
```

```json
{
  "title": "Count exhibitions for each gallery",
  "kind": "SELECT",
  "presenter": "Kaashvi",
  "sql": "SELECT gallery_id, COUNT(*) AS total_exhibitions\nFROM exhibition\nGROUP BY gallery_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "gallery_id",
      "total_exhibitions"
    ],
    "rows": [
      {
        "gallery_id": 1,
        "total_exhibitions": 3
      },
      {
        "gallery_id": 2,
        "total_exhibitions": 1
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "exhibitions",
  "query_id": "select3"
}
```

## Kaashvi · Find exhibitions in Mumbai galleries

```sql
SELECT title
FROM exhibition
WHERE gallery_id IN (
    SELECT gallery_id FROM gallery WHERE city = 'Mumbai'
);
```

```json
{
  "title": "Find exhibitions in Mumbai galleries",
  "kind": "SELECT",
  "presenter": "Kaashvi",
  "sql": "SELECT title\nFROM exhibition\nWHERE gallery_id IN (\n    SELECT gallery_id FROM gallery WHERE city = 'Mumbai'\n)",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "title"
    ],
    "rows": [
      {
        "title": "Light and Memory"
      },
      {
        "title": "Colour and Memory"
      },
      {
        "title": "New Perspectives"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "exhibitions",
  "query_id": "select4"
}
```

## Kaashvi · Format exhibition opening dates

```sql
SELECT title, TO_CHAR(start_date, 'DD-MM-YYYY') AS opening_date
FROM exhibition;
```

```json
{
  "title": "Format exhibition opening dates",
  "kind": "SELECT",
  "presenter": "Kaashvi",
  "sql": "SELECT title, TO_CHAR(start_date, 'DD-MM-YYYY') AS opening_date\nFROM exhibition",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "title",
      "opening_date"
    ],
    "rows": [
      {
        "title": "Light and Memory",
        "opening_date": "01-11-2026"
      },
      {
        "title": "Colour and Memory",
        "opening_date": "01-10-2026"
      },
      {
        "title": "Quiet Places",
        "opening_date": "01-11-2026"
      },
      {
        "title": "New Perspectives",
        "opening_date": "01-02-2027"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "exhibitions",
  "query_id": "select5"
}
```

## Gaurav · Create a demonstration record

```sql
INSERT INTO auction (auction_id, gallery_id, title, "DATE")
VALUES (:record_id, 1, :value, DATE '2026-12-15');
```

```json
{
  "title": "Create a demonstration record",
  "kind": "INSERT",
  "presenter": "Gaurav",
  "sql": "INSERT INTO auction (auction_id, gallery_id, title, \"DATE\")\nVALUES (:record_id, 1, :value, DATE '2026-12-15')",
  "binds": {
    "record_id": 100147,
    "value": "Student Auction"
  },
  "before": {
    "columns": [
      "auction_id",
      "gallery_id",
      "title",
      "date",
      "venue",
      "description",
      "status"
    ],
    "rows": [],
    "truncated": false
  },
  "result": {
    "columns": [
      "auction_id",
      "gallery_id",
      "title",
      "date",
      "venue",
      "description",
      "status"
    ],
    "rows": [
      {
        "auction_id": 100147,
        "gallery_id": 1,
        "title": "Student Auction",
        "date": "2026-12-15",
        "venue": null,
        "description": null,
        "status": "draft"
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "auctions",
  "query_id": "insert"
}
```

## Gaurav · Update that record

```sql
UPDATE auction
SET title = :value
WHERE auction_id = :record_id;
```

```json
{
  "title": "Update that record",
  "kind": "UPDATE",
  "presenter": "Gaurav",
  "sql": "UPDATE auction\nSET title = :value\nWHERE auction_id = :record_id",
  "binds": {
    "record_id": 100147,
    "value": "Student Auction revised"
  },
  "before": {
    "columns": [
      "auction_id",
      "gallery_id",
      "title",
      "date",
      "venue",
      "description",
      "status"
    ],
    "rows": [
      {
        "auction_id": 100147,
        "gallery_id": 1,
        "title": "Student Auction",
        "date": "2026-12-15",
        "venue": null,
        "description": null,
        "status": "draft"
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "auction_id",
      "gallery_id",
      "title",
      "date",
      "venue",
      "description",
      "status"
    ],
    "rows": [
      {
        "auction_id": 100147,
        "gallery_id": 1,
        "title": "Student Auction revised",
        "date": "2026-12-15",
        "venue": null,
        "description": null,
        "status": "draft"
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "auctions",
  "query_id": "update"
}
```

## Gaurav · Delete that demonstration record

```sql
DELETE FROM auction
WHERE auction_id = :record_id;
```

```json
{
  "title": "Delete that demonstration record",
  "kind": "DELETE",
  "presenter": "Gaurav",
  "sql": "DELETE FROM auction\nWHERE auction_id = :record_id",
  "binds": {
    "record_id": 100147
  },
  "before": {
    "columns": [
      "auction_id",
      "gallery_id",
      "title",
      "date",
      "venue",
      "description",
      "status"
    ],
    "rows": [
      {
        "auction_id": 100147,
        "gallery_id": 1,
        "title": "Student Auction revised",
        "date": "2026-12-15",
        "venue": null,
        "description": null,
        "status": "draft"
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "auction_id",
      "gallery_id",
      "title",
      "date",
      "venue",
      "description",
      "status"
    ],
    "rows": [],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "auctions",
  "query_id": "delete"
}
```

## Gaurav · Search auctions by title

```sql
SELECT auction_id, title, status
FROM auction
WHERE title LIKE :search;
```

```json
{
  "title": "Search auctions by title",
  "kind": "SELECT",
  "presenter": "Gaurav",
  "sql": "SELECT auction_id, title, status\nFROM auction\nWHERE title LIKE :search",
  "binds": {
    "search": "%%"
  },
  "before": null,
  "result": {
    "columns": [
      "auction_id",
      "title",
      "status"
    ],
    "rows": [
      {
        "auction_id": 1,
        "title": "Autumn Contemporary",
        "status": "open"
      },
      {
        "auction_id": 2,
        "title": "Winter Preview",
        "status": "draft"
      },
      {
        "auction_id": 3,
        "title": "Recent Acquisitions",
        "status": "closed"
      },
      {
        "auction_id": 100018,
        "title": "Student Auction Preview — revised",
        "status": "draft"
      },
      {
        "auction_id": 100097,
        "title": "Transaction demonstration 100096",
        "status": "closed"
      },
      {
        "auction_id": 100081,
        "title": "Presentation Auction 100075",
        "status": "closed"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "auctions",
  "query_id": "select1"
}
```

## Gaurav · Show the lots in each auction

```sql
SELECT a.title, l.lot_number
FROM auction a
JOIN auction_lot l ON a.auction_id = l.auction_id;
```

```json
{
  "title": "Show the lots in each auction",
  "kind": "SELECT",
  "presenter": "Gaurav",
  "sql": "SELECT a.title, l.lot_number\nFROM auction a\nJOIN auction_lot l ON a.auction_id = l.auction_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "title",
      "lot_number"
    ],
    "rows": [
      {
        "title": "Autumn Contemporary",
        "lot_number": 1
      },
      {
        "title": "Autumn Contemporary",
        "lot_number": 2
      },
      {
        "title": "Winter Preview",
        "lot_number": 1
      },
      {
        "title": "Winter Preview",
        "lot_number": 2
      },
      {
        "title": "Recent Acquisitions",
        "lot_number": 1
      },
      {
        "title": "Recent Acquisitions",
        "lot_number": 2
      },
      {
        "title": "Recent Acquisitions",
        "lot_number": 3
      },
      {
        "title": "Presentation Auction 100075",
        "lot_number": 1
      },
      {
        "title": "Transaction demonstration 100096",
        "lot_number": 1
      },
      {
        "title": "Transaction demonstration 100096",
        "lot_number": 2
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "auctions",
  "query_id": "select2"
}
```

## Gaurav · Count lots for each auction

```sql
SELECT auction_id, COUNT(*) AS total_lots
FROM auction_lot
GROUP BY auction_id;
```

```json
{
  "title": "Count lots for each auction",
  "kind": "SELECT",
  "presenter": "Gaurav",
  "sql": "SELECT auction_id, COUNT(*) AS total_lots\nFROM auction_lot\nGROUP BY auction_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "auction_id",
      "total_lots"
    ],
    "rows": [
      {
        "auction_id": 1,
        "total_lots": 2
      },
      {
        "auction_id": 2,
        "total_lots": 2
      },
      {
        "auction_id": 3,
        "total_lots": 3
      },
      {
        "auction_id": 100081,
        "total_lots": 1
      },
      {
        "auction_id": 100097,
        "total_lots": 2
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "auctions",
  "query_id": "select3"
}
```

## Gaurav · Find lots belonging to open auctions

```sql
SELECT lot_id, lot_number
FROM auction_lot
WHERE auction_id IN (
    SELECT auction_id FROM auction WHERE status = 'open'
);
```

```json
{
  "title": "Find lots belonging to open auctions",
  "kind": "SELECT",
  "presenter": "Gaurav",
  "sql": "SELECT lot_id, lot_number\nFROM auction_lot\nWHERE auction_id IN (\n    SELECT auction_id FROM auction WHERE status = 'open'\n)",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "lot_id",
      "lot_number"
    ],
    "rows": [
      {
        "lot_id": 101,
        "lot_number": 1
      },
      {
        "lot_id": 102,
        "lot_number": 2
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "auctions",
  "query_id": "select4"
}
```

## Gaurav · Show starting prices in rupees

```sql
SELECT lot_id, ROUND(starting_price / 100, 2) AS starting_price_inr
FROM auction_lot;
```

```json
{
  "title": "Show starting prices in rupees",
  "kind": "SELECT",
  "presenter": "Gaurav",
  "sql": "SELECT lot_id, ROUND(starting_price / 100, 2) AS starting_price_inr\nFROM auction_lot",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "lot_id",
      "starting_price_inr"
    ],
    "rows": [
      {
        "lot_id": 101,
        "starting_price_inr": 50000
      },
      {
        "lot_id": 102,
        "starting_price_inr": 30000
      },
      {
        "lot_id": 201,
        "starting_price_inr": 45000
      },
      {
        "lot_id": 202,
        "starting_price_inr": 25000
      },
      {
        "lot_id": 301,
        "starting_price_inr": 40000
      },
      {
        "lot_id": 302,
        "starting_price_inr": 30000
      },
      {
        "lot_id": 303,
        "starting_price_inr": 20000
      },
      {
        "lot_id": 100082,
        "starting_price_inr": 50000
      },
      {
        "lot_id": 100098,
        "starting_price_inr": 50000
      },
      {
        "lot_id": 100099,
        "starting_price_inr": 10000
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "auctions",
  "query_id": "select5"
}
```

## Shanil · Create a demonstration record

```sql
INSERT INTO bidder (bidder_id, name, email)
VALUES (:record_id, :value, :email);
```

```json
{
  "title": "Create a demonstration record",
  "kind": "INSERT",
  "presenter": "Shanil",
  "sql": "INSERT INTO bidder (bidder_id, name, email)\nVALUES (:record_id, :value, :email)",
  "binds": {
    "record_id": 100156,
    "value": "Demo Bidder",
    "email": "demo-100156@atelier.example"
  },
  "before": {
    "columns": [
      "bidder_id",
      "name",
      "email",
      "phone",
      "address"
    ],
    "rows": [],
    "truncated": false
  },
  "result": {
    "columns": [
      "bidder_id",
      "name",
      "email",
      "phone",
      "address"
    ],
    "rows": [
      {
        "bidder_id": 100156,
        "name": "Demo Bidder",
        "email": "demo-100156@atelier.example",
        "phone": null,
        "address": null
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "bidders",
  "query_id": "insert"
}
```

## Shanil · Update that record

```sql
UPDATE bidder
SET name = :value
WHERE bidder_id = :record_id;
```

```json
{
  "title": "Update that record",
  "kind": "UPDATE",
  "presenter": "Shanil",
  "sql": "UPDATE bidder\nSET name = :value\nWHERE bidder_id = :record_id",
  "binds": {
    "record_id": 100156,
    "value": "Demo Bidder revised"
  },
  "before": {
    "columns": [
      "bidder_id",
      "name",
      "email",
      "phone",
      "address"
    ],
    "rows": [
      {
        "bidder_id": 100156,
        "name": "Demo Bidder",
        "email": "demo-100156@atelier.example",
        "phone": null,
        "address": null
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "bidder_id",
      "name",
      "email",
      "phone",
      "address"
    ],
    "rows": [
      {
        "bidder_id": 100156,
        "name": "Demo Bidder revised",
        "email": "demo-100156@atelier.example",
        "phone": null,
        "address": null
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "bidders",
  "query_id": "update"
}
```

## Shanil · Delete that demonstration record

```sql
DELETE FROM bidder
WHERE bidder_id = :record_id;
```

```json
{
  "title": "Delete that demonstration record",
  "kind": "DELETE",
  "presenter": "Shanil",
  "sql": "DELETE FROM bidder\nWHERE bidder_id = :record_id",
  "binds": {
    "record_id": 100156
  },
  "before": {
    "columns": [
      "bidder_id",
      "name",
      "email",
      "phone",
      "address"
    ],
    "rows": [
      {
        "bidder_id": 100156,
        "name": "Demo Bidder revised",
        "email": "demo-100156@atelier.example",
        "phone": null,
        "address": null
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "bidder_id",
      "name",
      "email",
      "phone",
      "address"
    ],
    "rows": [],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "bidders",
  "query_id": "delete"
}
```

## Shanil · Search bidders by name

```sql
SELECT bidder_id, name, email
FROM bidder
WHERE name LIKE :search;
```

```json
{
  "title": "Search bidders by name",
  "kind": "SELECT",
  "presenter": "Shanil",
  "sql": "SELECT bidder_id, name, email\nFROM bidder\nWHERE name LIKE :search",
  "binds": {
    "search": "%%"
  },
  "before": null,
  "result": {
    "columns": [
      "bidder_id",
      "name",
      "email"
    ],
    "rows": [
      {
        "bidder_id": 1,
        "name": "Maya Sharma",
        "email": "maya@atelier.example"
      },
      {
        "bidder_id": 2,
        "name": "Arjun Patel",
        "email": "arjun@atelier.example"
      },
      {
        "bidder_id": 3,
        "name": "Sara Khan",
        "email": "sara@atelier.example"
      },
      {
        "bidder_id": 100101,
        "name": "Transaction Demo Bidder",
        "email": "transaction-100100@atelier.example"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "bidders",
  "query_id": "select1"
}
```

## Shanil · Show bids with bidder names

```sql
SELECT r.name, b.bid_amount / 100 AS amount_inr
FROM bidder r
JOIN bid b ON r.bidder_id = b.bidder_id;
```

```json
{
  "title": "Show bids with bidder names",
  "kind": "SELECT",
  "presenter": "Shanil",
  "sql": "SELECT r.name, b.bid_amount / 100 AS amount_inr\nFROM bidder r\nJOIN bid b ON r.bidder_id = b.bidder_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "name",
      "amount_inr"
    ],
    "rows": [
      {
        "name": "Maya Sharma",
        "amount_inr": 50000
      },
      {
        "name": "Maya Sharma",
        "amount_inr": 35000
      },
      {
        "name": "Maya Sharma",
        "amount_inr": 55000
      },
      {
        "name": "Maya Sharma",
        "amount_inr": 30000
      },
      {
        "name": "Maya Sharma",
        "amount_inr": 20000
      },
      {
        "name": "Maya Sharma",
        "amount_inr": 50000000
      },
      {
        "name": "Maya Sharma",
        "amount_inr": 65000
      },
      {
        "name": "Maya Sharma",
        "amount_inr": 15000
      },
      {
        "name": "Maya Sharma",
        "amount_inr": 60000
      },
      {
        "name": "Arjun Patel",
        "amount_inr": 55000
      },
      {
        "name": "Arjun Patel",
        "amount_inr": 30000
      },
      {
        "name": "Arjun Patel",
        "amount_inr": 40000
      },
      {
        "name": "Arjun Patel",
        "amount_inr": 45000
      },
      {
        "name": "Arjun Patel",
        "amount_inr": 25000
      },
      {
        "name": "Sara Khan",
        "amount_inr": 70000
      },
      {
        "name": "Transaction Demo Bidder",
        "amount_inr": 70000
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "bidders",
  "query_id": "select2"
}
```

## Shanil · Count bids for each bidder

```sql
SELECT bidder_id, COUNT(*) AS total_bids
FROM bid
GROUP BY bidder_id;
```

```json
{
  "title": "Count bids for each bidder",
  "kind": "SELECT",
  "presenter": "Shanil",
  "sql": "SELECT bidder_id, COUNT(*) AS total_bids\nFROM bid\nGROUP BY bidder_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "bidder_id",
      "total_bids"
    ],
    "rows": [
      {
        "bidder_id": 1,
        "total_bids": 9
      },
      {
        "bidder_id": 2,
        "total_bids": 5
      },
      {
        "bidder_id": 3,
        "total_bids": 1
      },
      {
        "bidder_id": 100101,
        "total_bids": 1
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "bidders",
  "query_id": "select3"
}
```

## Shanil · Find bidders who placed a bid

```sql
SELECT name
FROM bidder
WHERE bidder_id IN (
    SELECT bidder_id FROM bid
);
```

```json
{
  "title": "Find bidders who placed a bid",
  "kind": "SELECT",
  "presenter": "Shanil",
  "sql": "SELECT name\nFROM bidder\nWHERE bidder_id IN (\n    SELECT bidder_id FROM bid\n)",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "name"
    ],
    "rows": [
      {
        "name": "Maya Sharma"
      },
      {
        "name": "Arjun Patel"
      },
      {
        "name": "Sara Khan"
      },
      {
        "name": "Transaction Demo Bidder"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "bidders",
  "query_id": "select4"
}
```

## Shanil · Show bidder emails in lowercase

```sql
SELECT name, LOWER(email) AS email
FROM bidder;
```

```json
{
  "title": "Show bidder emails in lowercase",
  "kind": "SELECT",
  "presenter": "Shanil",
  "sql": "SELECT name, LOWER(email) AS email\nFROM bidder",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "name",
      "email"
    ],
    "rows": [
      {
        "name": "Maya Sharma",
        "email": "maya@atelier.example"
      },
      {
        "name": "Arjun Patel",
        "email": "arjun@atelier.example"
      },
      {
        "name": "Sara Khan",
        "email": "sara@atelier.example"
      },
      {
        "name": "Transaction Demo Bidder",
        "email": "transaction-100100@atelier.example"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "bidders",
  "query_id": "select5"
}
```

## Ashutosh · Create a demonstration record

```sql
INSERT INTO art_expert (expert_id, name)
VALUES (:record_id, :value);
```

```json
{
  "title": "Create a demonstration record",
  "kind": "INSERT",
  "presenter": "Ashutosh",
  "sql": "INSERT INTO art_expert (expert_id, name)\nVALUES (:record_id, :value)",
  "binds": {
    "record_id": 100165,
    "value": "Demo Expert"
  },
  "before": {
    "columns": [
      "expert_id",
      "name",
      "specialization",
      "email",
      "phone"
    ],
    "rows": [],
    "truncated": false
  },
  "result": {
    "columns": [
      "expert_id",
      "name",
      "specialization",
      "email",
      "phone"
    ],
    "rows": [
      {
        "expert_id": 100165,
        "name": "Demo Expert",
        "specialization": null,
        "email": null,
        "phone": null
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "experts",
  "query_id": "insert"
}
```

## Ashutosh · Update that record

```sql
UPDATE art_expert
SET name = :value
WHERE expert_id = :record_id;
```

```json
{
  "title": "Update that record",
  "kind": "UPDATE",
  "presenter": "Ashutosh",
  "sql": "UPDATE art_expert\nSET name = :value\nWHERE expert_id = :record_id",
  "binds": {
    "record_id": 100165,
    "value": "Demo Expert revised"
  },
  "before": {
    "columns": [
      "expert_id",
      "name",
      "specialization",
      "email",
      "phone"
    ],
    "rows": [
      {
        "expert_id": 100165,
        "name": "Demo Expert",
        "specialization": null,
        "email": null,
        "phone": null
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "expert_id",
      "name",
      "specialization",
      "email",
      "phone"
    ],
    "rows": [
      {
        "expert_id": 100165,
        "name": "Demo Expert revised",
        "specialization": null,
        "email": null,
        "phone": null
      }
    ],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "experts",
  "query_id": "update"
}
```

## Ashutosh · Delete that demonstration record

```sql
DELETE FROM art_expert
WHERE expert_id = :record_id;
```

```json
{
  "title": "Delete that demonstration record",
  "kind": "DELETE",
  "presenter": "Ashutosh",
  "sql": "DELETE FROM art_expert\nWHERE expert_id = :record_id",
  "binds": {
    "record_id": 100165
  },
  "before": {
    "columns": [
      "expert_id",
      "name",
      "specialization",
      "email",
      "phone"
    ],
    "rows": [
      {
        "expert_id": 100165,
        "name": "Demo Expert revised",
        "specialization": null,
        "email": null,
        "phone": null
      }
    ],
    "truncated": false
  },
  "result": {
    "columns": [
      "expert_id",
      "name",
      "specialization",
      "email",
      "phone"
    ],
    "rows": [],
    "truncated": false
  },
  "affected": 1,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "experts",
  "query_id": "delete"
}
```

## Ashutosh · Search experts by name

```sql
SELECT expert_id, name, specialization
FROM art_expert
WHERE name LIKE :search;
```

```json
{
  "title": "Search experts by name",
  "kind": "SELECT",
  "presenter": "Ashutosh",
  "sql": "SELECT expert_id, name, specialization\nFROM art_expert\nWHERE name LIKE :search",
  "binds": {
    "search": "%%"
  },
  "before": null,
  "result": {
    "columns": [
      "expert_id",
      "name",
      "specialization"
    ],
    "rows": [
      {
        "expert_id": 1,
        "name": "Dr. Anika Desai",
        "specialization": "Modern painting"
      },
      {
        "expert_id": 2,
        "name": "Daniel Roy",
        "specialization": "Contemporary art"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "experts",
  "query_id": "select1"
}
```

## Ashutosh · Show appraisals with expert names

```sql
SELECT e.name, p.estimated_value / 100 AS value_inr
FROM art_expert e
JOIN appraisal p ON e.expert_id = p.expert_id;
```

```json
{
  "title": "Show appraisals with expert names",
  "kind": "SELECT",
  "presenter": "Ashutosh",
  "sql": "SELECT e.name, p.estimated_value / 100 AS value_inr\nFROM art_expert e\nJOIN appraisal p ON e.expert_id = p.expert_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "name",
      "value_inr"
    ],
    "rows": [
      {
        "name": "Dr. Anika Desai",
        "value_inr": 65000
      },
      {
        "name": "Dr. Anika Desai",
        "value_inr": 80000
      },
      {
        "name": "Daniel Roy",
        "value_inr": 80000
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "experts",
  "query_id": "select2"
}
```

## Ashutosh · Count appraisals for each expert

```sql
SELECT expert_id, COUNT(*) AS total_appraisals
FROM appraisal
GROUP BY expert_id;
```

```json
{
  "title": "Count appraisals for each expert",
  "kind": "SELECT",
  "presenter": "Ashutosh",
  "sql": "SELECT expert_id, COUNT(*) AS total_appraisals\nFROM appraisal\nGROUP BY expert_id",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "expert_id",
      "total_appraisals"
    ],
    "rows": [
      {
        "expert_id": 1,
        "total_appraisals": 2
      },
      {
        "expert_id": 2,
        "total_appraisals": 1
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "experts",
  "query_id": "select3"
}
```

## Ashutosh · Find experts who performed an appraisal

```sql
SELECT name
FROM art_expert
WHERE expert_id IN (
    SELECT expert_id FROM appraisal
);
```

```json
{
  "title": "Find experts who performed an appraisal",
  "kind": "SELECT",
  "presenter": "Ashutosh",
  "sql": "SELECT name\nFROM art_expert\nWHERE expert_id IN (\n    SELECT expert_id FROM appraisal\n)",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "name"
    ],
    "rows": [
      {
        "name": "Dr. Anika Desai"
      },
      {
        "name": "Daniel Roy"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "experts",
  "query_id": "select4"
}
```

## Ashutosh · Show expert names in capital letters

```sql
SELECT UPPER(name) AS expert_name
FROM art_expert;
```

```json
{
  "title": "Show expert names in capital letters",
  "kind": "SELECT",
  "presenter": "Ashutosh",
  "sql": "SELECT UPPER(name) AS expert_name\nFROM art_expert",
  "binds": {},
  "before": null,
  "result": {
    "columns": [
      "expert_name"
    ],
    "rows": [
      {
        "expert_name": "DR. ANIKA DESAI"
      },
      {
        "expert_name": "DANIEL ROY"
      }
    ],
    "truncated": false
  },
  "affected": null,
  "transaction": "COMMIT",
  "database": "Oracle 11.2.0.2.0",
  "module_id": "experts",
  "query_id": "select5"
}
```
