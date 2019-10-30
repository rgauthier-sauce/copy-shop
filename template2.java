import io.appium.java_client.AppiumDriver;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.testobject.appium.junit.TestObjectTestResultWatcher;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.concurrent.TimeUnit;

public class AppiumTest {
    @Rule
    public TestObjectTestResultWatcher resultWatcher = new TestObjectTestResultWatcher();
    private AppiumDriver driver;


    @Before
    public void setUp() throws MalformedURLException {
        DesiredCapabilities caps = new DesiredCapabilities();

$capabilities


        driver = new IOSDriver(new URL("$domain"), caps);
        resultWatcher.setRemoteWebDriver(driver);

        System.out.println(driver.getSessionId().toString());
    }


    @Test
    public void emptyTest() throws InterruptedException {
    }

    @Test
    public void basicTest() throws InterruptedException {
        WebElement el;
        driver.manage().timeouts().implicitlyWait(30, TimeUnit.SECONDS);

$commands
    }

}