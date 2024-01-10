import com.azure.core.credential.AccessToken;
import com.azure.core.credential.BasicAuthenticationCredential;
import com.azure.core.credential.TokenRequestContext;
import reactor.core.publisher.Mono;

import java.time.OffsetDateTime;

public class FakeBasicAuthenticationCredential extends BasicAuthenticationCredential {

    public FakeBasicAuthenticationCredential(String username, String password) {
        super(username, password);
    }

    public Mono<AccessToken> getToken(TokenRequestContext context) {
        OffsetDateTime offset = OffsetDateTime.now();
        AccessToken token = new AccessToken("token", offset);
        return Mono.just(token);
    }

}
