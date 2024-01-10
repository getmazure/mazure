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
```
```
# Using Java
Configuration configuration = new Configuration()
        .put("java.net.useSystemProxies", "true")
        .put("http.proxyHost", "localhost")
        .put("http.proxyPort", "5005");

HttpClient nettyHttpClient = new NettyAsyncHttpClientBuilder()
        .configuration(configuration)
        .build();

AzureProfile profile = new AzureProfile(AzureEnvironment.AZURE);
BasicAuthenticationCredential credential = new FakeBasicAuthenticationCredential("test", "pass");
AzureResourceManager azure = AzureResourceManager
    .configure()
    .withHttpClient(nettyHttpClient)
    .authenticate(credential, profile)
    .withDefaultSubscription();
```
```
// Note that you can call specify the HTTPS_PROXY when invocing the tests
// But if maven needs to download anything else, Mazure will not able to serve those requests
HTTPS_PROXY=http://localhost:5005 mvn test -Djava.net.useSystemProxies=true
```
```
# Using .NET
REQUESTS_CA_BUNDLE=/path/to/ca.crt HTTPS_PROXY=http://localhost:5005 dotnet test MyProject
```

