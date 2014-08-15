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

dn = 'CN=ms-Exch-Transport-Inbound-Settings,CN=Schema,CN=Configuration,DC=zentyal,DC=lan'
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
        print record.oc_ldif()

except ldap.LDAPError, e:
        print e

finally:
    adconn.unbind()
