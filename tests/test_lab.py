import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
from lab import ROOT, connect, load_fixture, report, run_query, timestamp


class SQLTests(unittest.TestCase):
    def setUp(self):
        self.db = connect()
        self.db.executemany("INSERT INTO users VALUES (?, 'test', 'human')", [(u,) for u in ('alex','b','c','d')])

    def tearDown(self):
        self.db.close()

    def auth(self, i, t, user='alex', ip='192.0.2.1', outcome='failure'):
        self.db.execute('INSERT INTO auth_events VALUES (?, ?, ?, ?, ?)', (i,t,user,ip,outcome))

    def failures(self):
        for i in range(5):
            self.auth(str(i),i)

    def test_spray_distinct_accounts(self):
        for i in range(6): self.auth(str(i),i)
        self.assertEqual(run_query(self.db,'01_password_spray'),[])
        for i,u in enumerate(('b','c','d')): self.auth(u,10+i,u)
        rows=run_query(self.db,'01_password_spray')
        self.assertEqual([(r['anchor_event_id'],r['distinct_users']) for r in rows],[('d',4)])

    def test_spray_window_boundary(self):
        for i,u in enumerate(('alex','b','c')): self.auth(str(i),i,u)
        self.auth('d',300,'d')
        self.assertEqual(len(run_query(self.db,'01_password_spray')),1)
        self.db.execute("UPDATE auth_events SET event_time=301 WHERE event_id='d'")
        self.assertEqual(run_query(self.db,'01_password_spray'),[])

    def test_sources_are_separate(self):
        for i,u in enumerate(('alex','b','c','d')): self.auth(str(i),i,u,ip=f'192.0.2.{i+1}')
        self.assertEqual(run_query(self.db,'01_password_spray'),[])

    def test_success_boundary(self):
        self.failures()
        self.auth('s',300,outcome='success')
        self.assertEqual(run_query(self.db,'02_success_after_failures')[0]['preceding_failures'],5)
        self.db.execute("UPDATE auth_events SET event_time=301 WHERE event_id='s'")
        self.assertEqual(run_query(self.db,'02_success_after_failures'),[])

    def test_same_time_is_not_preceding(self):
        self.failures()
        self.auth('s',4,outcome='success')
        self.assertEqual(run_query(self.db,'02_success_after_failures'),[])

    def test_success_pair_isolation(self):
        self.failures()
        self.auth('s1',10,user='b',outcome='success')
        self.auth('s2',10,ip='192.0.2.2',outcome='success')
        self.assertEqual(run_query(self.db,'02_success_after_failures'),[])

    def test_access_does_not_double_count(self):
        self.failures()
        self.auth('s1',10,outcome='success')
        self.auth('s2',20,outcome='success')
        for i,t in enumerate((30,40)):
            self.db.execute("INSERT INTO access_events VALUES (?,?,'alex','192.0.2.1','export',6000000)",(str(i),t))
        row=run_query(self.db,'03_access_after_flagged_login')[0]
        self.assertEqual((row['access_count'],row['total_bytes']),(2,12000000))

    def test_access_time_and_byte_boundaries(self):
        self.failures()
        self.auth('s',10,outcome='success')
        for i,t in enumerate((10,610,611)):
            self.db.execute("INSERT INTO access_events VALUES (?,?,'alex','192.0.2.1','export',10000000)",(str(i),t))
        row=run_query(self.db,'03_access_after_flagged_login')[0]
        self.assertEqual(row['access_count'],1)
        self.assertEqual(row['total_bytes'],10000000)
        self.assertEqual(run_query(self.db,'03_access_after_flagged_login',{'min_bytes':10000001}),[])

    def test_foreign_key_and_constraints(self):
        for sql in ["INSERT INTO auth_events VALUES ('x',0,'unknown','ip','failure')",
                    "INSERT INTO auth_events VALUES ('x',0,'alex','ip','other')",
                    "INSERT INTO access_events VALUES ('x',0,'alex','ip','file',-1)"]:
            with self.subTest(sql=sql), self.assertRaises(sqlite3.IntegrityError): self.db.execute(sql)

    def test_parameters_not_sql(self):
        self.assertEqual(run_query(self.db,'04_account_timeline',{'user_id':"alex' OR 1=1 --"}),[])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM users').fetchone()[0],4)

    def test_config_and_query_allowlist(self):
        with self.assertRaises(ValueError): run_query(self.db,'../schema')
        with self.assertRaises(ValueError): run_query(self.db,'01_password_spray',{'min_users':0})

    def test_timestamp_contract(self):
        self.assertEqual(timestamp('2026-01-01T01:00:00+01:00'),timestamp('2026-01-01T00:00:00Z'))
        for text in ('2026-01-01T00:00:00','2026-01-01T00:00:00.1Z'):
            with self.assertRaises(ValueError): timestamp(text)

    def test_timeline_preserves_sources(self):
        self.auth('same-id',10,outcome='success')
        self.db.execute("INSERT INTO access_events VALUES ('same-id',10,'alex','192.0.2.1','file',0)")
        rows=run_query(self.db,'04_account_timeline')
        self.assertEqual([r['source'] for r in rows],['authentication','resource_access'])

    def test_fixture_matches_expected(self):
        with connect() as db:
            load_fixture(db)
            expected=json.loads((ROOT/'examples/expected-results.json').read_text(encoding='utf-8'))
            self.assertEqual(report(db),expected)

    def test_cli(self):
        result=subprocess.run([sys.executable,str(ROOT/'lab.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        expected=json.loads((ROOT/'examples/expected-results.json').read_text(encoding='utf-8'))
        self.assertEqual(json.loads(result.stdout),expected)
        bad=subprocess.run([sys.executable,str(ROOT/'lab.py'),'--min-bytes','0'],capture_output=True,text=True)
        self.assertEqual(bad.returncode,2)
        self.assertEqual(bad.stdout,'')


if __name__ == '__main__': unittest.main()
