import re

import pytest

from atelier import create_app
from atelier.db import get_db
from atelier.queries import QUERIES
from atelier.registry import READONLY, TABLES, paise


@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING':True, 'DATABASE':str(tmp_path/'web.sqlite'), 'SECRET_KEY':'test-only-key'})


@pytest.fixture
def client(app):
    return app.test_client()


def csrf(client, path='/login'):
    page=client.get(path).get_data(as_text=True)
    match=re.search(r'name="csrf_token"\s+value="([^"]+)"',page)
    assert match, f'No CSRF token in {path}'
    return match.group(1)


def login(client,email='admin@atelier.example',password='AdminDemo!2026'):
    response=client.post('/login',data={'email':email,'password':password,'csrf_token':csrf(client)})
    assert response.status_code==302
    return response


def post(client,path,data=None,token_page='/staff'):
    payload=dict(data or {},csrf_token=csrf(client,token_page))
    return client.post(path,data=payload)


def test_public_pages_and_filters(client):
    for path in ('/','/collection','/collection/1','/collection/12','/exhibitions','/exhibitions/1','/auctions','/auctions/1','/auctions/2','/auctions/3','/login'):
        assert client.get(path).status_code==200,path
    page=client.get('/collection?q=Monsoon').get_data(as_text=True)
    assert 'Monsoon Reverie' in page and 'A Quiet Morning' not in page
    assert client.get('/collection?q=nonexistent').status_code==200
    assert client.get('/collection/999').status_code==404
    assert client.get('/nonsense').status_code==404


def test_dummy_accounts_and_permissions(app,client):
    assert client.get('/staff').status_code==302
    assert client.post('/login',data={'email':'admin@atelier.example','password':'wrong'}).status_code==400
    for name in ('maya','arjun','sara'):
        login(client,f'{name}@atelier.example','BidderDemo!2026')
        assert client.get('/account').status_code==200
        assert client.get('/staff').status_code==403
        assert post(client,'/staff/lots/101/close',token_page='/account').status_code==403
        post(client,'/logout',token_page='/account')
    login(client)
    assert client.get('/staff').status_code==200
    assert client.get('/account').status_code==403
    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) FROM user_account').fetchone()[0]==4


def test_all_staff_views_and_forms(client):
    login(client)
    for table in TABLES:
        assert client.get(f'/staff/data/{table}').status_code==200,table
        if table not in READONLY:
            assert client.get(f'/staff/data/{table}/new').status_code==200,table
    assert client.get('/staff/data/user_account').status_code==404
    assert client.get('/staff/data/bid/new').status_code==403
    for query in QUERIES:
        page=client.get('/staff/reports?query='+query['id'])
        assert page.status_code==200,query['id']
    assert client.get('/staff/reports?query=DROP%20TABLE%20artist').status_code==404


def test_staff_crud_and_constraint_feedback(app,client):
    login(client)
    response=post(client,'/staff/data/artist/new',{'name':'Test Artist','birth_date':'1990-01-01','nationality':'Indian','biography':'A test profile.'})
    assert response.status_code==302
    with app.app_context():
        aid=get_db().execute("SELECT artist_id FROM artist WHERE name='Test Artist'").fetchone()[0]
    assert client.get(f'/staff/data/artist/{aid}/edit').status_code==200
    assert post(client,f'/staff/data/artist/{aid}/edit',{'name':'Updated Artist','birth_date':'1990-01-01'}).status_code==302
    assert post(client,f'/staff/data/artist/{aid}/delete').status_code==302
    assert post(client,'/staff/data/artist/1/delete').status_code==302
    with app.app_context():
        assert get_db().execute('SELECT 1 FROM artist WHERE artist_id=1').fetchone()
        assert get_db().execute('SELECT 1 FROM artist WHERE artist_id=?',(aid,)).fetchone() is None
    bad=post(client,'/staff/data/exhibition/new',{'title':'Impossible dates','gallery_id':'1','curator_id':'1','start_date':'2026-03-05','end_date':'2026-03-01'})
    assert bad.status_code==400
    assert b'database rule' in bad.data


def test_full_presentation_workflow(app,client):
    login(client)
    assert post(client,'/staff/data/artwork/new',{'artist_id':'1','title':'The Presentation Work','year_created':'2026','medium':'Oil on canvas','dimensions':'80 x 60 cm','description':'Created during the walkthrough.','image_path':'images/artwork-12.webp'}).status_code==302
    with app.app_context():
        aid=get_db().execute("SELECT artwork_id FROM artwork WHERE title='The Presentation Work'").fetchone()[0]
    assert post(client,'/staff/data/exhibition_artwork/new',{'exhibition_id':'3','artwork_id':str(aid),'display_position':'East wall'}).status_code==302
    assert post(client,'/staff/data/appraisal/new',{'artwork_id':str(aid),'expert_id':'1','appraisal_date':'2026-10-27','estimated_value':'90000','notes':'Presentation appraisal.'}).status_code==302
    assert post(client,'/staff/data/authentication/new',{'artwork_id':str(aid),'expert_id':'1','certificate_no':'DEMO-TEST-01','authentication_date':'2026-10-27','result':'Authentic','notes':'Presentation certificate.'}).status_code==302
    assert post(client,'/staff/data/auction_lot/new',{'auction_id':'2','artwork_id':str(aid),'lot_number':'3','starting_price':'50000','reserve_price':'60000'}).status_code==302
    assert post(client,'/staff/auctions/2/open').status_code==302
    with app.app_context():
        lot_id=get_db().execute('SELECT lot_id FROM auction_lot WHERE artwork_id=?',(aid,)).fetchone()[0]
    post(client,'/logout')
    login(client,'maya@atelier.example','BidderDemo!2026')
    assert post(client,f'/lots/{lot_id}/bid',{'amount':'65000'},'/account').status_code==302
    post(client,'/logout',token_page='/account')
    login(client,'sara@atelier.example','BidderDemo!2026')
    assert post(client,f'/lots/{lot_id}/bid',{'amount':'70000.50'},'/account').status_code==302
    post(client,'/logout',token_page='/account')
    login(client)
    assert post(client,f'/staff/lots/{lot_id}/close').status_code==302
    assert post(client,f'/staff/lots/{lot_id}/close').status_code==302
    with app.app_context():
        sale=get_db().execute('''SELECT s.sale_id,s.sale_price,c.bidder_id FROM sale s JOIN collector c ON c.collector_id=s.collector_id
            JOIN bid b ON b.bid_id=s.bid_id WHERE b.lot_id=?''',(lot_id,)).fetchone()
        assert tuple(sale)[1:]==(7000050,3)
        sid=sale['sale_id']
    assert post(client,f'/staff/sales/{sid}/payment',{'status':'completed'}).status_code==302
    with app.app_context():
        query=next(q for q in QUERIES if q['id']=='collectors')
        spending={r['collector']:r['total_spent_inr'] for r in get_db().execute(query['sql'])}
        assert spending['Sara Khan']==70000.5
    assert client.get(f'/collection/{aid}').status_code==200


def test_preset_reports_fixture_and_persistence(app):
    with app.app_context():
        db=get_db()
        queries={q['id']:q['sql'] for q in QUERIES}
        revenue=list(db.execute(queries['revenue']))
        assert sum(r['revenue_inr'] for r in revenue)==55000
        collectors={r['collector']:r['total_spent_inr'] for r in db.execute(queries['collectors'])}
        assert collectors=={'Maya Sharma':55000.0,'Arjun Patel':0.0}
        with db:
            db.execute("UPDATE artist SET biography='Persistence check' WHERE artist_id=1")
    another=create_app({'TESTING':True,'DATABASE':app.config['DATABASE'],'SECRET_KEY':'test-only-key'})
    with another.app_context():
        assert get_db().execute('SELECT biography FROM artist WHERE artist_id=1').fetchone()[0]=='Persistence check'


def test_money_parser_rejects_invalid_and_fractional_paise():
    assert paise('70000.50')==7000050
    for amount in ('NaN','Infinity','-1','1.001','bad','1000000000000'):
        with pytest.raises(ValueError):
            paise(amount)
