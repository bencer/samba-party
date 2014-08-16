"""
requirements:
apt-get install heimdal-clients python-ldap libsasl2-modules-gssapi-heimdal openchangeclient
samba-tool domain exportkeytab samba.keytab --principal='Administrator'
kinit -t samba.keytab Administrator
"""

import ldap
import ldap.sasl
import ldif, ldap.modlist
import ldaphelper

schemadn =  'CN=Schema,CN=Configuration,DC=zentyal,DC=lan'
dn = 'CN=ms-Exch-Transport-Settings,' + schemadn
filter = '(objectclass=*)'
attrs = ['*']

try:
    adconn = ldap.initialize('ldap://localhost', trace_level=0)
    adconn.protocol_version = 3
    adconn.set_option(ldap.OPT_REFERRALS,0)
    sasl_auth = ldap.sasl.sasl({},'GSSAPI')
    adconn.sasl_interactive_bind_s("", sasl_auth)

    raw_res = adconn.search_s( dn, ldap.SCOPE_BASE, filter, attrs )
    res = ldaphelper.get_search_results( raw_res )
    for record in res:
        print record.oc_ldif(schemadn)
        subattrs = record.get_attr('mayContain')
        if not subattrs:
           continue
        for subattr in subattrs:
            filter = "(lDAPDisplayName=%s)" % subattr
            sub_raw_res = adconn.search_s( schemadn, ldap.SCOPE_SUBTREE, filter, attrs )
            sub_res = ldaphelper.get_search_results( sub_raw_res )
            for subrecord in sub_res:
                print subrecord.oc_ldif(schemadn)

except ldap.LDAPError, e:
        print e

finally:
    adconn.unbind()
