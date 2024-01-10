import com.azure.core.credential.BasicAuthenticationCredential;
import com.azure.core.http.HttpClient;
import com.azure.core.http.ProxyOptions;
import com.azure.core.http.netty.NettyAsyncHttpClientBuilder;
import com.azure.core.http.rest.PagedIterable;
import com.azure.core.management.AzureEnvironment;
import com.azure.core.management.profile.AzureProfile;
import com.azure.core.util.Configuration;
import com.azure.resourcemanager.AzureResourceManager;
import com.azure.resourcemanager.resources.fluent.models.LocationInner;
import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

import java.net.InetSocketAddress;
import java.util.List;
import java.util.stream.Collectors;

public class AccountManagementTest extends TestCase {

    public AccountManagementTest( String testName )
    {
        super( testName );
    }

    public static Test suite()
    {
        return new TestSuite( AccountManagementTest.class );
    }

    private void exampleProxyCreation() {
        ProxyOptions proxyOptions = new ProxyOptions(ProxyOptions.Type.HTTP, new InetSocketAddress("localhost", 8888));

        HttpClient nettyHttpClient = new NettyAsyncHttpClientBuilder()
                .proxy(proxyOptions)
                .build();
    }

    public void testListLocations()
    {

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
        PagedIterable<LocationInner> x = azure
            .genericResources()
            .manager()
            .subscriptionClient()
            .getSubscriptions()
            .listLocations("a1ffc958-d2c7-493e-9f1e-125a0477f536", true, com.azure.core.util.Context.NONE);

        List<LocationInner> y = x.stream().collect(Collectors.toList());
        assertEquals(83, y.size());
    }
}
