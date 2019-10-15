import org.junit.*;
import org.openqa.selenium.*;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.RemoteWebDriver;
import java.net.URL;
import java.util.concurrent.TimeUnit;

import com.saucelabs.common.SauceOnDemandAuthentication;
import com.saucelabs.common.SauceOnDemandSessionIdProvider;
import com.saucelabs.junit.SauceOnDemandTestWatcher;

public class SeleniumTest implements SauceOnDemandSessionIdProvider {

    public static String username = "$username";
    public static String accesskey = "$access_key";

    protected WebDriver driver;
    private String sessionId;

    public SauceOnDemandAuthentication authentication = new SauceOnDemandAuthentication(username, accesskey);

    @Rule
    public SauceOnDemandTestWatcher resultReportingTestWatcher = new SauceOnDemandTestWatcher(this, authentication);

    @Before
    public void setUp() throws Exception {
        DesiredCapabilities caps = new DesiredCapabilities();

$capabilities

        URL url = new URL("https://" + username+ ":" + accesskey + "@$domain/wd/hub");
        System.out.println(url);
        System.out.println(caps);
        this.driver = new RemoteWebDriver(url, caps);
        sessionId = (((RemoteWebDriver) driver).getSessionId()).toString();
        System.out.println("Session ID: " + sessionId);
    }

    @Test
    public void emptyTest() throws InterruptedException {
        // run this for only testing capabilities
    }

    @Test
    public void simpleTest() throws InterruptedException {
    }

    // ----------

    @After
    public void tearDown() throws Exception {
        driver.quit();
    }

    @Override
    public String getSessionId() {
        return sessionId;
    }

}