# coding:utf8
"""

Author: ilcwd
"""
from kuaipan.utils.mysql import (
    escape,
)


# a value indicate no value in it.
NOTSET = object()


def my_escape(s):
    if isinstance(s, (int, long)):
        return "%d" % s

    return "'%s'" % escape(s)


class BaseBO(object):
    pass


class BaseMapper(object):
    pass


class BaseQuery(object):
    class _MapperGenerator(object):
        def __init__(self, prefix):
            self.select_from = [prefix]
            self.where_condition = []
            self.tailing = []

        def limit(self, n, offset=0):
            n, offset = int(n), int(offset)
            if offset:
                self.tailing.append("LIMIT %d,%d" % (offset, n))
            self.tailing.append("LIMIT %d" % n)
            return self

        def sql(self):
            if self.where_condition:
                ll = self.select_from + ['WHERE', ' AND '.join(self.where_condition)] + self.tailing
                return ' '.join(ll)
            return ' '.join(self.select_from + self.tailing)

        __str__ = sql

        def op(self, op, key, value):
            self.where_condition.append("`%s`%s%s" % (key, op, my_escape(value)))
            return self

        def and_equal_to(self, key, value):
            return self.op("=", key, value)

        def and_greater_than(self, key, value):
            return self.op(">", key, value)

        def and_less_than(self, key, value):
            return self.op("<", key, value)

        def and_greater_equal(self, key, value):
            return self.op(">=", key, value)

        def and_less_equal(self, key, value):
            return self.op("<=", key, value)

        def and_not_equal(self, key, value):
            return self.op("!=", key, value)

        def and_not_null(self, key):
            self.where_condition.append("`%s` IS NOT NULL" % key)
            return self

        def and_is_null(self, key):
            self.where_condition.append("`%s` IS NULL" % key)
            return self

    def __init__(self, columns, table):
        self.columns = columns
        self._table = table
        self._select_columns = ','.join(('`%s`' % col for col in self.columns))

    def table(self):
        return self._table

    def select(self):
        select_sql = (
            "SELECT %s FROM `%s`"
            % (self._select_columns, self.table())
        )
        return self._MapperGenerator(select_sql)

    def update(self, dictobj):
        assert isinstance(dictobj, dict), ("MUST BE dict: %s", dictobj)
        for k in dictobj.iterkeys():
            if k not in self.columns:
                raise Exception("Unexpected key `%s`: %s" % (k, self.columns))

        sql_set = ','.join((("`%s`=%s" % (k, my_escape(v)))
                            for k, v in dictobj.iteritems()))
        update_sql = (
            "UPDATE `%s` SET %s"
            % (self.table(), sql_set)
        )
        return self._MapperGenerator(update_sql)

    def delete(self):
        delete_sql = (
            "DELETE FROM `%s`"
            % (self.table(),)
        )
        return self._MapperGenerator(delete_sql)

    def insert(self, dictobjs):
        if isinstance(dictobjs, dict):
            dictobjs = [dictobjs]

        keys = dictobjs[0].keys()
        keys_sql = ','.join(("`%s`" % k for k in keys))
        values = [("(%s)" % r)
                  for r in (','.join(my_escape(obj[k])
                                     for k in keys)
                            for obj in dictobjs)]
        values_sql = ','.join(values)

        insert_sql = (
            "INSERT INTO `%s`(%s) VALUES %s"
            % (self.table(), keys_sql, values_sql)
        )
        return self._MapperGenerator(insert_sql)


class BaseShardQuery(BaseQuery):
    def __init__(self, columns, table):
        super(BaseShardQuery, self).__init__(columns, table)
        self.index = None
        assert '%d' in self._table, "A shard query's table MUST include `%d` to set shard."

    def set_index(self, index):
        self.index = int(index)
        return self

    def table(self):
        if self.index is None:
            raise Exception("Call `set_index(index)` before you do any operations.")
        return self._table % self.index
