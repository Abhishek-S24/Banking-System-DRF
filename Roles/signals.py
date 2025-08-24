from .models import UserRole, UserPermission

def create_default_roles(sender, **kwargs):
    # Define permissions
    permissions = {
        "create_users": "Can create new users",
        "manage_users": "Can update or delete users",
        "view_users": "Can view user list and details",
        "view_all_transactions": "Can view all transactions",
        "view_all_accounts": "Can view all accounts",
        "manage_roles": "Can create/update/delete roles",
        "manage_permissions": "Can create/update/delete permissions",
        "export_excel": "Can export data to Excel",
        "initiate_transaction": "Can initiate fund transfers",
        "view_own_account": "Can view own accounts",
        "view_own_transactions": "Can view own transactions",
    }

    # Create permissions
    perm_objs = {}
    for code, desc in permissions.items():
        perm, _ = UserPermission.objects.get_or_create(
            code=code,
            defaults={"description": desc, "active": True}
        )
        perm_objs[code] = perm

    # Define roles with assigned permissions
    role_permissions = {
        "Admin": [
            "create_users", "manage_users", "view_users",
            "view_all_transactions", "view_all_accounts",
            "manage_roles", "manage_permissions", "export_excel"
        ],
        "Service Executive": [
            "view_users", "view_all_transactions",
            "view_all_accounts", "initiate_transaction"
        ],
        "Auditor": [
            "view_users", "view_all_transactions",
            "view_all_accounts", "export_excel"
        ],
        "Customer": [
            "view_own_account", "view_own_transactions",
            "initiate_transaction"
        ],
    }

    # Create roles and link permissions
    for role_name, perms in role_permissions.items():
        role, _ = UserRole.objects.get_or_create(name=role_name, defaults={"active": True})
        role.user_permissions.set([perm_objs[p] for p in perms])
