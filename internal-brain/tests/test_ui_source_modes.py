"""Source navigation metadata must match actual connector configuration."""
from fastapi.testclient import TestClient
from app import main, server


def test_demo_sources_are_labelled_and_have_no_external_links():
    with TestClient(server.app) as client:
        login = client.post('/api/login', json={'username':'jdoe','password':'demo'}).json()
        headers = {'Authorization':'Bearer ' + login['token']}
        session = client.get('/api/session', headers=headers).json()
        assert session['source_modes'] == {p:'simulated' for p in ('jira','confluence','slack','gdrive')}
        result = client.post('/api/ask', headers=headers,
            json={'question':"What's blocking the database migration?"}).json()
        assert result['citations']
        for citation in result['citations']:
            assert citation['source_mode'] == 'simulated'
            assert citation['url'] is None
        jira = next(c for c in result['citations'] if c['platform'] == 'jira')
        assert jira['status'] in {'Blocked','In Progress','Done','Open'}
        evidence = client.get(f"/api/evidence/{result['query_id']}/{jira['ref']}",headers=headers).json()
        assert evidence['url'] is None
        assert evidence['passages']


def test_only_confirmed_live_sources_get_external_links(monkeypatch):
    monkeypatch.setitem(main.state, 'source_modes', {'jira':'live', 'slack':'simulated'})
    for platform, url in [('jira','https://example.atlassian.net/browse/MIG-1'),
                          ('slack',None), ('gdrive',None)]:
        source={'platform':platform,'url':'https://example.atlassian.net/browse/MIG-1'}
        result=main._source_presentation(source)
        assert result['url'] == url
        assert source['url']  # Presentation does not mutate source snapshots.


def test_contractor_answer_does_not_gain_source_metadata():
    with TestClient(server.app) as client:
        login=client.post('/api/login',json={'username':'kim','password':'demo'}).json()
        response=client.post('/api/ask',headers={'Authorization':'Bearer '+login['token']},
            json={'question':'Show me the security incident report from the Q3 breach'}).json()
        assert response['status']=='no_answer'
        assert response['citations']==[]
