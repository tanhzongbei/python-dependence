#coding:utf8
"""

Author: ilcwd
"""

from kputils.mysql import (
    BaseDB,
    escape,
)
from kputils.mysqlmodel import BaseQuery

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


def test_generate_sql():
    testQuery = BaseQuery(['autoid', 'k', 'v', 'ctime'], 'test1')
    assert_equal(testQuery.delete().and_equal_to('autoid', 1).limit(10).sql(),
                 r'''DELETE FROM `test1` WHERE `autoid`=1 LIMIT 10''')

    assert_equal(testQuery.update({'k': 1, 'v': 2}).and_greater_equal("k", 1).and_less_than("k", 10).sql(),
                 r'''UPDATE `test1` SET `k`=1,`v`=2 WHERE `k`>=1 AND `k`<10''')

    assert_equal(testQuery.insert([{'k': 1, 'v': 2}, {'k': 2, 'v': "3'\""}]).sql(),
                 r'''INSERT INTO `test1`(`k`,`v`) VALUES (1,2),(2,'3\'\"')''')

    assert_equal(testQuery.select().and_less_than('k', 2).sql(),
                 r'''SELECT `autoid`,`k`,`v`,`ctime` FROM `test1` WHERE `k`<2''')


def test_escape():
    assert_equal(escape("你好"), "你好")
    assert_equal(escape(1), "1")
    assert_equal(escape(145678909876423456786L), "145678909876423456786")
    # assert_equal(escape(''' \x00\'\"\b\n\r\t\Z\\\%\_ '''), r" \0\'\"\b\n\r\Z\\%_ ")


def test_bench():
    import time

    testQuery = BaseQuery(['autoid', 'k', 'v', 'ctime'], 'test1')

    LOOP = 10000
    st = time.time()
    for i in xrange(LOOP):
        print testQuery.delete().and_equal_to('autoid', 1).limit(10)
    et = time.time()
    ct = et-st
    print "Cost %.2fs, rps %.2f" % (ct, LOOP/ct)

    testQuery.update({'k': 1, 'v': 2}).and_greater_equal("k", 1).and_less_than("k", 10).sql()
    testQuery.insert([{'k': 1, 'v': 2}, {'k': 2, 'v': "3'\""}]).sql()
    testQuery.select().and_less_than('k', 2).sql()


def test():
    mydb = BaseDB(myconfig)
    # another connection
    mydb2 = BaseDB(myconfig)

    _TEST_TABLE = '''
    DROP TABLE IF EXISTS `test1`;
    CREATE TABLE IF NOT EXISTS `test1` (
        autoid INT NOT NULL AUTO_INCREMENT,
        k VARCHAR(10) NOT NULL,
        v VARCHAR(100) NOT NULL,
        ctime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
        PRIMARY KEY (`autoid`),
        UNIQUE INDEX (`k`)
    )ENGINE=Innodb DEFAULT CHARSET='utf8';
    '''
    mydb.query(_TEST_TABLE)

    aid, rows = mydb.insert("INSERT INTO test1(k,v) VALUES(%s,%s)", ("aaa", "AAA"))
    assert aid == 1, "autoid MUST be 1"
    assert rows == 1, "insert 1 row"

    rows = mydb.execute("UPDATE test1 SET v=%s WHERE k=%s", ('BBB', 'aaa'))
    assert rows == 1, "update 1 row"

    # Read Committed
    values = mydb2.query("SELECT autoid, k, v FROM test1 LIMIT 10;")
    assert len(values) == 1, "only 1 record in table"
    aid, k, v = values[0]
    assert aid == 1 and k == 'aaa' and v == 'BBB', "result must be commit"

    # Cannot Read uncommitted
    with mydb.session() as (conn, cursor):
        cursor.execute("SELECT autoid, k, v FROM test1 WHERE k=%s", 'aaa')
        values = cursor.fetchall()
        assert len(values) == 1, "only 1 record in table"
        aid, k, v = values[0]
        assert aid == 1 and k == 'aaa' and v == 'BBB', "result must be commit"

        rows = cursor.execute("UPDATE test1 SET v=%s WHERE k=%s", ('CCC', 'aaa'))
        assert rows == 1

        # read uncommitted
        values = mydb2.query("SELECT autoid, k, v FROM test1 LIMIT 10;")
        assert len(values) == 1, "only 1 record in table"
        aid, k, v = values[0]
        assert aid == 1 and k == 'aaa' and v == 'BBB', "result is not be committed"

    values = mydb2.query("SELECT autoid, k, v FROM test1 LIMIT 10;")
    assert len(values) == 1, "only 1 record in table"
    aid, k, v = values[0]
    assert aid == 1 and k == 'aaa' and v == 'CCC', "result is committed"


def main():
    test()
    test_generate_sql()
    test_escape()
    print "FIN"


if __name__ == '__main__':
    main()
