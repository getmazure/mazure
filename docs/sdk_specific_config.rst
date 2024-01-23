.. _sdk_specific_config:

SDK Specific Configuration
==========================

Every SDK has a slightly different way to configure a proxy. Please see the examples below to get an idea how to do this in the language of your choice.

Have you found a different way to configure a proxy for a specific language, or want to contribute an example for another language, please see the `Edit on Github`-button at the top of the page.


.. contents::
    :local:


Python
------

The Azure SDK for Python needs the correct SSL certificate before it trusts the Mazure-proxy.

Download the certificate from our Github:
https://github.com/getmazure/mazure/blob/main/mazure/mazure_proxy/ca.crt

Run your tests like you normally would, but set the following environment variables:

.. sourcecode:: bash

    REQUESTS_CA_BUNDLE=/path/to/ca.crt HTTPS_PROXY=http://localhost:5005 pytest -sv tests/


Dotnet
------

The Azure SDK for DotNet needs to told that it can trust our certificate.

Configure a custom HTTP-client like this:

.. sourcecode:: csharp

    var handler = new HttpClientHandler();
    handler = new HttpClientHandler
        {
            ClientCertificateOptions = ClientCertificateOption.Manual,
            ServerCertificateCustomValidationCallback =
                (httpRequestMessage, cert, cetChain, policyErrors) => true
        };
    var blobClientOptions = new BlobClientOptions();
    blobClientOptions.Transport = new HttpClientTransport(handler);

    var blobServiceClient = new BlobServiceClient(
        new Uri("https://storage_account.blob.core.windows.net"),
        blobClientOptions
    );


.. warning:: Clients for other services may have a different way to configure the ClientOptions - see the Azure documentation for more details.

Setup the dotnet tests like you would normally:


.. sourcecode:: bash

    dotnet restore Application/


But configure the actual test execution to use the proxy:

.. sourcecode:: bash

    ALL_PROXY="http://localhost:5005" dotnet test Application/


CLI
---
The Azure CLI needs the Mazure SSL certificate to trust the proxy.

Download the certificate from our Github:
https://github.com/getmazure/mazure/blob/main/mazure/mazure_proxy/ca.crt

Run your tests like you normally would, but set the following environment variables:

.. sourcecode:: bash

    REQUESTS_CA_BUNDLE=/path/to/ca.crt HTTPS_PROXY=http://localhost:5005 az group list


Java
----

The Azure SDK for Java needs two things to connect to the Mazure-proxy:
 - The HTTP-Client needs to be configured to use our proxy, and
 - The Mazure SSL certificate needs to be added to the Java keytool

Download our SSL certificate from Github:
https://github.com/getmazure/mazure/blob/main/mazure/mazure_proxy/ca.crt

Add it to the keytool using this command:

.. sourcecode:: bash

    sudo keytool -import -noprompt -alias mazure -keystore $JAVA_HOME/lib/security/cacerts  -file path/to/ca.crt -storepass "changeit"


Configure your Azure tests to use a custom HTTP-client:

.. sourcecode:: java

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

