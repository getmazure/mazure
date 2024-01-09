# mazure
An easy tool to Mock the interactions with Azure SDK's in your application.


### Step 1: 
Download the Proxy's Certificate from Github:
...

### Step 2:
Start the Proxy:
...

### Step 3: 
Configure your tests to run against the Proxy:

```
# Using Python
REQUESTS_CA_BUNDLE=/path/to/ca.crt HTTPS_PROXY=http://localhost:5005 pytest -sv tests/

# Using Java
REQUESTS_CA_BUNDLE=/path/to/ca.crt HTTPS_PROXY=http://localhost:5005 mvn test

# Using .NET
REQUESTS_CA_BUNDLE=/path/to/ca.crt HTTPS_PROXY=http://localhost:5005 dotnet test MyProject
```

