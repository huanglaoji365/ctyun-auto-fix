"""云电脑入口识别与点击的轻量回归测试。"""

import importlib
import sys
import types
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

# 测试入口逻辑不需要启动 OCR、HTTP 或 Chromium，提供最小模块占位即可。
sys.modules.setdefault("ddddocr", types.ModuleType("ddddocr"))
sys.modules.setdefault("requests", types.ModuleType("requests"))
drission_page = types.ModuleType("DrissionPage")
drission_page.ChromiumOptions = type("ChromiumOptions", (), {})
drission_page.ChromiumPage = type("ChromiumPage", (), {})
sys.modules.setdefault("DrissionPage", drission_page)

pc_login = importlib.import_module("pc_login")


class FakeElement:
    def __init__(self, text="", inner_text=None):
        self.text = text
        self.inner_text = text if inner_text is None else inner_text
        self.scripts = []

    def run_js(self, script):
        self.scripts.append(script)
        if script.startswith("return"):
            return self.inner_text
        return None


class FakePage:
    def __init__(self, buttons):
        self.url = pc_login.DESKTOP_URL
        self.buttons = buttons

    def ele(self, _selector, timeout=None):
        return None

    def eles(self, selector):
        if selector == pc_login.DESKTOP_BUTTON_SELECTOR:
            return self.buttons
        return []


class DesktopEntryTests(unittest.TestCase):
    def test_recognizes_text_split_across_child_nodes(self):
        button = FakeElement("", "进入\nAI 云电脑")
        self.assertEqual(
            pc_login.get_desktop_state(FakePage([button])), "has_pc_button"
        )

    def test_single_rendered_button_is_safe_fallback(self):
        button = FakeElement("", "")
        self.assertEqual(
            pc_login.get_desktop_state(FakePage([button])), "has_pc_button"
        )

    def test_click_dispatches_bubbling_dom_event(self):
        button = FakeElement("进入AI云电脑")
        self.assertTrue(pc_login.click_enter_ai_pc(FakePage([button])))
        self.assertTrue(any("dispatchEvent" in script for script in button.scripts))
        self.assertTrue(any("bubbles: true" in script for script in button.scripts))


if __name__ == "__main__":
    unittest.main()
