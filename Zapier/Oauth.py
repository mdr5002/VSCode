authorization_base_url = (
    "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
)
client_id = "4ab2679a-ff8c-49c4-83eb-8b0770dcbd2d"
redirect_uri = "https://EmailAI.com/auth/callback"
scope = "Files.ReadWrite"

authorization_url = f"{authorization_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
print(
    f"Please go to the following URL to authorize the application: {authorization_url}"
)
