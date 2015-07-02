#coding:utf8
"""

Author: ilcwd
"""
import unittest
import threading
import time

from kuaipan.utils.mysql import (
    BaseDB,
    escape,
    OperationalError,
    is_lost_connection_exception,
    set_db_connection_idle_timeout,
)

import logging
rootlogger = logging.getLogger()
rootlogger.setLevel(logging.NOTSET)
rootlogger.addHandler(logging.StreamHandler())

myconfig = dict(
    host="10.0.3.184",
    db="test",
    user="kuaipan",
    passwd="r5G6KPtqcTjh1YBv",
    port=3306,
    charset="utf8"
)


def assert_equal(a, b, msg=''):
    if b != a:
        assert False, ("Expert (%s)`%s`, but (%s)`%s`: %s" % (type(a), a, type(b), b, msg))


class Test(unittest.TestCase):
    _DROP_TABLE = '''
    DROP TABLE IF EXISTS `test1`;
    '''
    _CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS `test1` (
        autoid INT NOT NULL AUTO_INCREMENT,
        k VARCHAR(100) NOT NULL,
        v VARCHAR(100) NOT NULL,
        ctime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
        PRIMARY KEY (`autoid`),
        UNIQUE INDEX (`k`)
    )ENGINE=Innodb DEFAULT CHARSET='utf8';
    '''

    def setUp(self):
        self.mydb = BaseDB(myconfig)

        self.mydb.execute(self._DROP_TABLE)
        self.mydb.execute(self._CREATE_TABLE)

    def tearDown(self):
        self.mydb.execute(self._DROP_TABLE)
        self.mydb.close()

    def test_basic(self):
        mydb = BaseDB(myconfig)
        mydb2 = BaseDB(myconfig)

        aid, rows = mydb.insert("INSERT INTO test1(k,v) VALUES('%s','%s')" % ("aaa", "AAA"))
        assert_equal(aid, 1, 'autoid')
        assert rows == 1, "insert 1 row"

        rows = mydb.execute("UPDATE test1 SET v='%s' WHERE k='%s'" % ('BBB', 'aaa'))
        assert rows == 1, "update 1 row"

        # Read Committed
        values = mydb2.query("SELECT autoid, k, v FROM test1 LIMIT 10;")
        assert len(values) == 1, "only 1 record in table"
        aid, k, v = values[0]
        assert aid == '1' and k == 'aaa' and v == 'BBB', ("result must be commit: %s" % values)

        # Cannot Read uncommitted
        with mydb.session() as conn:
            values = conn.query("SELECT autoid, k, v FROM test1 WHERE k='aaa'")
            assert len(values) == 1, "only 1 record in table"
            aid, k, v = values[0]
            assert aid == '1' and k == 'aaa' and v == 'BBB', "result must be commit"

            rows = conn.execute("UPDATE test1 SET v='%s' WHERE k='%s'" % ('CCC', 'aaa'))
            assert rows == 1

            # read uncommitted
            values = mydb2.query("SELECT autoid, k, v FROM test1 LIMIT 10;")
            assert len(values) == 1, "only 1 record in table"
            aid, k, v = values[0]
            assert aid == '1' and k == 'aaa' and v == 'BBB', ("result is not commit: %s" % values)

        values = mydb2.query("SELECT autoid, k, v FROM test1 LIMIT 10;")
        assert len(values) == 1, "only 1 record in table"
        aid, k, v = values[0]
        assert aid == '1' and k == 'aaa' and v == 'CCC', "result is committed"

    def test_rollback(self):
        k = 'test_rollback'
        mydb1 = BaseDB(myconfig)
        mydb2 = BaseDB(myconfig)
        autoid, rows = mydb1.insert("INSERT INTO test1(k,v) VALUES('%s', 1);" % escape(k))
        assert_equal(autoid, 1, "autoid")
        assert_equal(rows, 1, "rows")

        try:
            with mydb1.session() as conn:
                rows = conn.execute("UPDATE test1 SET v=2 WHERE k='%s'" % escape(k))
                assert_equal(rows, 1, "rows")

                raise Exception("I want a rollback")
        except Exception as e:
            if str(e) != "I want a rollback":
                raise
        else:
            assert False, "Must get an exception."

        v, = mydb1.query_one("SELECT v FROM test1 WHERE k='%s'" % escape(k))
        assert_equal(v, '1')
        v, = mydb2.query_one("SELECT v FROM test1 WHERE k='%s'" % escape(k))
        assert_equal(v, '1')

    def test_thread_safety(self):
        mydb = BaseDB(myconfig)
        LOOP = 100
        THREAD = 10

        def work():
            for i in xrange(LOOP):
                mydb.query("SHOW TABLES")

        threads = []
        for tn in xrange(THREAD):
            t = threading.Thread(target=work)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def test_thread_transaction(self):
        myk = 'test_multi_thread_inserttion'
        autoid, rows = self.mydb.insert("INSERT INTO test1(k,v) VALUES('%s', 1);" % escape(myk))
        assert_equal(autoid, 1, "autoid")
        assert_equal(rows, 1, "rows")

        LOOP = 50
        THREAD = 10

        def work():
            mydb = BaseDB(myconfig)
            for i in xrange(LOOP):
                with mydb.session() as conn:
                    # MUST use `FOR UPDATE` to block reading
                    _, v = conn.query_one("SELECT autoid,v FROM test1 WHERE k='%s' FOR UPDATE;" % escape(myk))

                    rows2 = conn.execute("UPDATE test1 SET v=%d WHERE k='%s'" % (int(v)+1, escape(myk)))
                    assert rows2 == 1, (rows2, 1)

        threads = []
        for tn in xrange(THREAD):
            t = threading.Thread(target=work)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        aid, v2 = self.mydb.query_one("SELECT autoid, v FROM test1 WHERE k='%s'" % escape(myk))
        assert_equal(int(v2), THREAD*LOOP+1, "finally v")
        assert_equal(int(aid), 1, "autoid")

    def test_lost_connection(self):
        mydb = BaseDB(myconfig)
        mydb2 = BaseDB(myconfig)
        tid1, = mydb.query_one("SELECT CONNECTION_ID();")

        mydb2.execute("KILL %d" % int(tid1))

        # connection is lost!!
        # but it can recover quietly.
        tid2, = mydb.query_one("SELECT CONNECTION_ID();")
        assert tid1 != tid2, ("Connection ID must be difference: %s", (tid1, tid2))

    def test_lost_connection_during_session(self):
        k = 'test_rollback'
        mydb1 = BaseDB(myconfig)
        mydb2 = BaseDB(myconfig)
        autoid, rows = mydb1.insert("INSERT INTO test1(k,v) VALUES('%s', 1);" % escape(k))
        assert_equal(autoid, 1, "autoid")
        assert_equal(rows, 1, "rows")

        tid1, = mydb1.query_one("SELECT CONNECTION_ID();")
        try:
            with mydb1.session() as conn:
                rows = conn.execute("UPDATE test1 SET v=2 WHERE k='%s'" % escape(k))
                assert_equal(rows, 1, "rows")

                # create lost connection exception
                mydb2.execute("KILL %d" % int(tid1))

                # this statement will raise exception
                conn.execute("UPDATE test1 SET v=3 WHERE k='%s'" % escape(k))

        except OperationalError as e:
            if not is_lost_connection_exception(e):
                raise

        else:
            assert False, "Must get an exception."

        # nothing is committed
        v, = mydb1.query_one("SELECT v FROM test1 WHERE k='%s'" % escape(k))
        assert_equal(v, '1')
        v, = mydb2.query_one("SELECT v FROM test1 WHERE k='%s'" % escape(k))
        assert_equal(v, '1')

    def test_idle_connection(self):
        set_db_connection_idle_timeout(1)

        def _connection_id_in_processlist(connid):
            db = BaseDB(myconfig)
            processlist = db.query("SHOW PROCESSLIST;")
            conns = set(int(x[0]) for x in processlist )
            return int(connid) in conns

        mydb = BaseDB(myconfig)
        tid1, = mydb.query_one("SELECT CONNECTION_ID();")
        assert _connection_id_in_processlist(tid1)
        time.sleep(1)
        tid2, = mydb.query_one("SELECT CONNECTION_ID();")
        assert not _connection_id_in_processlist(tid1)
        assert _connection_id_in_processlist(tid2)

        set_db_connection_idle_timeout(600)

    def test_thread_safety2(self):
        mydb = BaseDB(myconfig)
        THREAD = 10
        result = []
        
        def work():
            # print "#Thread(%s), DB(%s), Conn(%s)#" % (threading.currentThread().ident, id(mydb), id(mydb.conn))
            result.append((id(mydb), id(mydb.conn)))

        threads = []
        for tn in xrange(THREAD):
            t = threading.Thread(target=work)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        assert_equal(len(result), THREAD, 'len of result')
        assert_equal(len(set(y for x, y in result)), THREAD, 'different connection')
        assert_equal(len(set(x for x, y in result)), 1, 'different BaseDB object')


def main():
    unittest.main()

if __name__ == '__main__':
    main()
