import re
import ldif
import commands
from StringIO import StringIO

schemadn =  'CN=Schema,CN=Configuration,DC=zentyal,DC=lan'
schemavar = '${SCHEMADN}'
base64_attrs = ['schemaIDGUID', 'objectGUID', 'attributeSecurityGUID']
del_attrs = ['instanceType', 'msDS-IntId', 'objectGUID', 'uSNChanged',
             'uSNCreated', 'whenChanged', 'whenCreated']

def get_search_results(results):
    res = []

    if type(results) == tuple and len(results) == 2 :
        (code, arr) = results
    elif type(results) == list:
        arr = results

    if len(results) == 0:
        return res

    for item in arr:
        res.append( LDAPSearchResult(item) )

    return res

def guid_format(attr, ldif_str):
    guid = re.findall("%s::\s([\w,=,+,/]+)" % attr, ldif_str)[0]
    new_guid = commands.getstatusoutput('/usr/bin/schemaIDGUID %s' % guid)[1]
    ldif_str = ldif_str.replace("%s::" % attr, "%s:" % attr)
    ldif_str = ldif_str.replace(guid, new_guid)
    return ldif_str

class LDAPSearchResult:
    """A class to model LDAP results
    """

    dn = ''

    def __init__(self, entry_tuple):
        (dn, attrs) = entry_tuple
        if dn:
            self.dn = dn
        else:
            return

        self.attrs = attrs

    def del_attr(self, attr_name):
        try:
            del self.attrs[attr_name]
        except KeyError:
            pass

    def get_attr(self, attr_name):
        return self.attrs[attr_name]

    def set_attr(self, attr_name, attr_value):
        self.attrs[attr_name] = attr_value

    def del_internal_attrs(self):
        for attr in del_attrs:
            self.del_attr(attr)

    def to_ldif(self):
        out = StringIO()
        ldif_out = ldif.LDIFWriter(out, base64_attrs = base64_attrs, cols = 999)
        self.del_internal_attrs()
        ldif_out.unparse(self.dn, self.attrs)
        return out.getvalue()

    def oc_ldif(self):
        ldif_str = self.to_ldif()
        ldif_str = ldif_str.replace(schemadn, schemavar)
        ldif_str = guid_format('schemaIDGUID', ldif_str)
        ldif_str = guid_format('attributeSecurityGUID', ldif_str)
        return ldif_str

