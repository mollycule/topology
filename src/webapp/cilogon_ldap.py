import ldap3


def get_contact_cilogon_id_map(global_data):
    """ return contacts dict, limited to users with a CILogonID """
    contacts = global_data.get_contacts_data().users_by_id;
    return { k: v for k, v in contacts.items() if v.cilogon_id is not None }


# cilogon ldap query constants
_ldap_url = "ldaps://ldap.cilogon.org"
_username = "uid=readonly_user,ou=system,o=OSG,o=CO,dc=cilogon,dc=org"
_basedn   = "o=OSG,o=CO,dc=cilogon,dc=org"


def get_cilogon_ldap_id_map(ldappass):
    """ return dict of cilogon ldap data for each CILogonID, with the
        structure: {CILogonID: { "dn": dn, "data": data }, ...} """
    server = ldap3.Server(_ldap_url)
    conn = ldap3.Connection(server, _username, ldappass)
    if not conn.bind():
        return None  # connection failure
    conn.search(_basedn, '(voPersonID=*)', attributes=['*'])
    result_data = [ (e.entry_dn, e.entry_attributes_as_dict)
                    for e in conn.entries ]
    conn.unbind()
    return {
        voPersonID: { "dn": dn, "data": data }
        for dn, data in result_data
        if "voPersonID" in data
        for voPersonID  in data["voPersonID"]
    }


def cilogon_id_map_to_ssh_keys(m):
    """ convert id map (as returned by get_cilogon_ldap_id_map) to a dict with
        structure: {CILogonID: [sshPublicKey, ...], ...} for each id that has
        ssh public keys defined """
    return {
        k: v['data']['sshPublicKey']
        for k, v in m.items()
        if 'sshPublicKey' in v['data']
    }

