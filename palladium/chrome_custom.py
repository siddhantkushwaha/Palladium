import os
import time
import random
import logging

from collections import Sized

from selenium.webdriver import Chrome, ChromeOptions

from palladium import params


class ChromeCustom(Chrome):
    logs_dir = os.path.join('.', 'logs')

    def __init__(self, headless=True, logs_dir=None):
        self.logs_dir = os.path.join(os.getcwd() if logs_dir is None else logs_dir, 'logs')

        chrome_options = ChromeOptions()

        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.binary_location = params.chromebinary

        super().__init__(params.chromedriver, options=chrome_options)

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def find_element_by_css_selector(self, css_selector):
        return self.attempt(lambda: super(Chrome, self).find_element_by_css_selector(css_selector))

    def find_elements_by_css_selector(self, css_selector):
        return self.attempt(lambda: super(Chrome, self).find_elements_by_css_selector(css_selector))

    def find_element_by_xpath(self, xpath):
        return self.attempt(lambda: super(Chrome, self).find_element_by_xpath(xpath))

    def find_elements_by_xpath(self, xpath):
        return self.attempt(lambda: super(Chrome, self).find_elements_by_xpath(xpath))

    def attempt(
            self,
            method,
            wait_time=4,
            total_attempts=4,
    ):
        os.makedirs(self.logs_dir, exist_ok=True)
        for i in range(total_attempts):
            try:
                val = method()
                if isinstance(val, Sized) and len(val) == 0:
                    raise Exception('Empty sized iterable.')
                return val
            except Exception as exp:
                time.sleep(wait_time)
                if i + 1 == total_attempts:
                    logging.exception(exp)
                    name = ''.join([str(i) for i in [random.randint(0, 9) for j in range(12)]])
                    self.get_screenshot_as_file(os.path.join(self.logs_dir, f'screenshot_{name}.png'))
                    raise Exception(f'Attempt failed for method. {method}')

    def highlight(self, element, color='red', border=5, effect_time=5):
        def apply_style(s):
            element._parent.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                           element, s)

        original_style = element.get_attribute('style')
        apply_style("border: {0}px solid {1};".format(border, color))
        time.sleep(effect_time)
        apply_style(original_style)
