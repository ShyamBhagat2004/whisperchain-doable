# what each role is allowed to do
role_permissions = {
    "Sender": ["send_message", "flag_message", "issue_token"],
    "Recipient": ["receive_message", "flag_message"],
    "Moderator": ["view_flagged", "view_logs"],
    "Sysadmin": ["manage_users", "view_logs"]
}

# checks if a role is allowed to do something
def has_permission(role, action):
    allowed_actions = role_permissions.get(role, [])
    return action in allowed_actions
