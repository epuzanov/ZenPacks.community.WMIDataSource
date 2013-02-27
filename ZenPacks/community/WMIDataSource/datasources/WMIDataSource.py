################################################################################
#
# This program is part of the WMIDataSource Zenpack for Zenoss.
# Copyright (C) 2009-2013 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""WMIDataSource

Defines attributes for how a datasource will be graphed
and builds the nessesary DEF and CDEF statements for it.

$Id: WMIDataSource.py,v 2.6 2013/02/27 23:44:48 egor Exp $"""

__version__ = "$Revision: 2.6 $"[11:-2]

from Products.ZenModel.RRDDataSource import RRDDataSource
from ZenPacks.community.SQLDataSource.datasources import SQLDataSource
from AccessControl import ClassSecurityInfo, Permissions

import re
PATHPAT = re.compile("^(?:([^\. ]+):)?([^\.\: ]+)(?:\.(.+))?", re.I)
CSTMPL = "'pywmidb',user='%s',password='%s',host='%s',namespace='%s'"

class WMIDataSource(SQLDataSource.SQLDataSource):

    ZENPACKID = 'ZenPacks.community.WMIDataSource'

    sourcetypes = ('WMI',)
    sourcetype = 'WMI'
    namespace = 'root/cimv2'
    wql = ''

    _properties = RRDDataSource._properties + (
        {'id':'namespace', 'type':'string', 'mode':'w'},
        {'id':'wql', 'type':'string', 'mode':'w'},
        )


    # Screen action bindings (and tab definitions)
    factory_type_information = ( 
    {
        'immediate_view' : 'editWMIDataSource',
        'actions'        :
        (
            { 'id'            : 'edit'
            , 'name'          : 'Data Source'
            , 'action'        : 'editWMIDataSource'
            , 'permissions'   : ( Permissions.view, )
            },
        )
    },
    )


    def getDescription(self):
        return self.wql


    def zmanage_editProperties(self, REQUEST=None):
        'add some validation'
        if REQUEST:
            self.namespace = REQUEST.get('namespace', '')
            self.wql = REQUEST.get('wql', '')
        return RRDDataSource.zmanage_editProperties(self, REQUEST)


    def getConnectionString(self, context, namespace=''):
        if not namespace: namespace = self.getCommand(context, self.namespace)
        if hasattr(context, 'device'):
            device = context.device()
        else:
            device = context
        user = getattr(device, 'zWinUser', '')
        password = getattr(device, 'zWinPassword', '')
        host = getattr(device,'zWmiProxy','') or getattr(device,'manageIp','')
        return CSTMPL%(user, password, host, namespace)


    def getQueryInfo(self, context):
        try:
            sql = self.getCommand(context, self.wql)
            if sql.upper().startswith('SELECT '):
                try: sqlp, kbs = self.parseSqlQuery(sql)
                except: sqlp, kbs = sql, {}
                return sql, sqlp, kbs, self.getConnectionString(context)
            namespace, classname, where = PATHPAT.match(sql).groups('')
            cs = self.getConnectionString(context, namespace)
            cols = set([dp.getAliasNames() and dp.getAliasNames()[0] or dp.id \
                                            for dp in self.getRRDDataPoints()])
            try:
                if r'\\' in where: where = where.encode('string-escape')
                kbs = eval('(lambda **kws:kws)(%s)'%where)
            except: kbs = {}
            if cols: cols.update(set(kbs.keys()))
            sqlp = 'SELECT %s FROM %s'%(','.join(cols) or '*', classname)
            if where: where = ' WHERE %s'%where.replace(',', ' AND ')
            sql = ''.join((sqlp, where))
            if kbs: return sql, sqlp, kbs, cs
            else: return sql, sql, kbs, cs
        except: return '', '', {}, ''
