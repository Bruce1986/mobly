from mobly import base_test
from mobly import test_runner
from mobly.controllers import android_device

import datetime
import time


class FemasHrTest(base_test.BaseTestClass):
  """Automates clock in/out for the Femas HR app."""

  SCREEN_WIDTH = 1080
  SCREEN_HEIGHT = 2400

  def setup_class(self):
    self.ads = self.register_controller(android_device)
    self.dut = self.ads[0]

    self.center_x = self.SCREEN_WIDTH // 2
    self.nav_y = self.SCREEN_HEIGHT * 18 // 19
    self.nav_item_width = self.SCREEN_WIDTH // 5
    self.nav_item2_x = self.nav_item_width + self.nav_item_width // 2

    self.checkin_x = 320
    self.checkin_y = 2250
    self.checkout_x = 750
    self.checkout_y = 2250
    self.confirm_x = 530
    self.confirm_y = 2000

    self.swipe_start_y = self.SCREEN_HEIGHT * 3 // 4
    self.swipe_end_y = self.SCREEN_HEIGHT // 4

  def _tap(self, x, y, wait_secs=1):
    self.dut.log.info("Tapping coordinates (%s, %s)", x, y)
    self.dut.take_screenshot(self.log_path, f"before_tap_{x}x{y}")
    process = self.dut.adb.shell(["input", "tap", str(x), str(y)])
    if process.ret_code != 0:
      self.dut.log.error(f"Tapping coordinates ({x}, {y}) failed: {process.stderr}")
      return  # Or raise an exception, depending on the desired behavior
    self.dut.log.info("Tapped (%s, %s), waiting %s seconds", x, y, wait_secs)
    time.sleep(wait_secs)
    self.dut.take_screenshot(self.log_path, f"after_tap_{x}x{y}")

  def _power_on_device(self):
    self.dut.log.info("Power key press to wake device")
    self.dut.take_screenshot(self.log_path, "before_power_key")
    self.dut.adb.shell(["input", "keyevent", "KEYCODE_POWER"])
    time.sleep(1)
    self.dut.take_screenshot(self.log_path, "after_power_key")

  def _swipe_up_to_unlock(self):
    self.dut.log.info("Swiping up to unlock")
    self.dut.take_screenshot(self.log_path, "before_swipe_up")
    process = self.dut.adb.shell(
        [
            "input",
            "swipe",
            str(self.center_x),
            str(self.swipe_start_y),
            str(self.center_x),
            str(self.swipe_end_y),
        ]
    )
    if process.ret_code != 0:
      self.dut.log.error(f"Swiping up to unlock failed: {process.stderr}")
      return  # Or raise an exception, depending on the desired behavior
    )
    time.sleep(1)
    self.dut.take_screenshot(self.log_path, "after_swipe_up")

  def _launch_app(self, package):
    self.dut.log.info("Launching app: %s", package)
    self.dut.take_screenshot(self.log_path, f"before_launch_{package}")
    process = self.dut.adb.shell(
        [
            "monkey",
            "-p",
            package,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ]
    )
    if process.ret_code != 0:
      self.dut.log.error(f"Launching app {package} failed: {process.stderr}")
      return  # Or raise an exception, depending on the desired behavior
    )
    time.sleep(2)
    self.dut.take_screenshot(self.log_path, f"after_launch_{package}")

  def test_checkin_checkout(self):
    self._power_on_device()
    self._swipe_up_to_unlock()
    self._launch_app("com.femascloud.femashr")
    self._tap(self.nav_item2_x, self.nav_y, 3)
    self._tap(self.confirm_x, self.confirm_y, 1)

    hour = datetime.datetime.now().hour
    if hour < 12:
      self.dut.log.info("Morning: Tap left-side button for check-in")
      self._tap(self.checkin_x, self.checkin_y, 1)
    else:
      self.dut.log.info("Afternoon: Tap right-side button for check-out")
      self._tap(self.checkout_x, self.checkout_y, 1)


if __name__ == "__main__":
  test_runner.main()
