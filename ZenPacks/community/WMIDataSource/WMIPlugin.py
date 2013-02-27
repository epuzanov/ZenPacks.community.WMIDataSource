################################################################################
#
# This program is part of the WMIDataSource Zenpack for Zenoss.
# Copyright (C) 2009-2013 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""WMIPlugin

wrapper for PythonPlugin

$Id: WMIPlugin.py,v 2.2 2013/02/27 23:44:01 egor Exp $"""

__version__ = "$Revision: 2.2 $"[11:-2]

from ZenPacks.community.SQLDataSource.SQLPlugin import SQLPlugin
CSTMPL = "'pywmidb',user='%s',password='%s',host='%s',namespace='%s'"

class WMIPlugin(SQLPlugin):
    """
    A WMIPlugin defines a native Python collection routine and a parsing
    method to turn the returned data structure into a datamap. A valid
    WMIPlugin must implement the process method.
    """

    deviceProperties = SQLPlugin.deviceProperties + (
        'zWinUser',
        'zWinPassword',
        'zWmiProxy',
    )

    def prepareQueries(self, device):
        queries = self.queries(device)
        user = getattr(device, 'zWinUser', '')
        password = getattr(device, 'zWinPassword', '')
        host = getattr(device,'zWmiProxy','') or getattr(device,'manageIp','')
        squeries = {}
        for tname, query in queries.iteritems():
            sql, kbs, namespace, columns = query
            if not sql.lower().startswith('select '):
                sql = 'SELECT %s FROM %s'%('*', sql)
                if kbs:
                    kbstrings = []
                    for kbn, kbv in kbs.iteritems():
                        if type(kbv) == str: kbv = '"%s"'%kbv
                        kbstrings.append('%s=%s'%(kbn, kbv))
                    sql = sql + ' WHERE %s'%' AND '.join(kbstrings)
            cs = CSTMPL%(user, password, host, namespace)
            columns = dict(zip(columns.values(), columns.keys()))
            squeries[tname] = (sql, kbs, cs, columns)
        return squeries
