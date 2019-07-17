import org.junit.*;
import org.openqa.selenium.*;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.RemoteWebDriver;
import java.net.URL;

public class SeleniumTest {

    public static String username = "$username";
    public static String accesskey = "$access_key";

    protected WebDriver driver;
    private String sessionId;

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

    @After
    public void tearDown() throws Exception {
        driver.quit();
    }

    @Test
    public void simpleTest() throws InterruptedException {
    }

}