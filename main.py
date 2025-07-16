import data

PASSWORD = b"password"

data.add_service(PASSWORD, "google", "name", "password")

print(data.get_credentials(PASSWORD, "google"))
print(data.get_services(PASSWORD))

data.remove_service(PASSWORD, "google")

print(data.get_credentials(PASSWORD, "google"))
