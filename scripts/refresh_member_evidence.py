"""Verify just the changed member presets and refresh their genuine Oracle outputs."""
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from atelier import create_app
from atelier.assignment_queries import MODULES
from atelier.db import get_db
from atelier.presentation import events


def token(response):
    return re.search(rb'name="csrf_token" value="([^"]+)"',response.data).group(1).decode()


def main():
    app=create_app({'TESTING':True})
    checks=[]
    with app.test_client() as client:
        page=client.get('/login')
        logged_in=client.post('/login',data=dict(csrf_token=token(page),email='admin@atelier.example',password='AdminDemo!2026'))
        assert logged_in.status_code==302
        for mod in MODULES:
            for query in mod['queries']:
                page=client.get('/staff/presentation?module='+mod['id'])
                assert mod['presenter'].encode() in page.data
                response=client.post('/staff/presentation/execute/'+mod['id']+'/'+query['id'],
                    data=dict(csrf_token=token(page),presenter=mod['presenter']),follow_redirects=True)
                assert response.status_code==200 and b'executed in Oracle' in response.data,(mod['presenter'],query['id'])
                checks.append(mod['presenter']+'/'+query['id'])
        with client.session_transaction() as state:
            workspace=state['oracle_workspace']
        with app.app_context():
            evidence=events(get_db(),workspace)
            assert len(evidence)==40
            for mod in MODULES:
                own=[e for e in evidence if e['module_id']==mod['id']]
                assert len(own)==8 and all(e['presenter']==mod['presenter'] for e in own)
                assert all(e['affected']==1 for e in own if e['kind']!='SELECT')
                assert own[2]['kind']=='DELETE' and own[2]['result']['rows']==[]
        output=dict(engine='Oracle',workspace=workspace,records=40,members=[m['presenter'] for m in MODULES],checks=checks)
        (ROOT/'docs/assignment/MEMBER_VERIFICATION.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    print('All 40 simplified statements executed through Flask on Oracle, with the five real presenter names.')


if __name__=='__main__':
    main()
