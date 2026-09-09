import random
import time
import math
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


class HumanSimulator:
    def __init__(self, driver, use_native_cursor=False):
        """
        use_native_cursor: if True, attempts to use pyautogui to move the REAL
        OS mouse cursor (visible on screen) instead of Selenium's synthetic
        in-browser pointer events. Requires pyautogui + a working display
        (X server / DISPLAY set). Falls back to Selenium ActionChains if
        unavailable (e.g. headless server, no X display).
        """
        self.driver = driver
        self.current_x = 0
        self.current_y = 0
        self.use_native_cursor = False
        self.pyautogui = None

        if use_native_cursor:
            try:
                import pyautogui  # imported lazily - triggers mouseinfo/X connection
                self.pyautogui = pyautogui
                self.use_native_cursor = True
            except Exception as e:
                # Catches ImportError (not installed) AND runtime errors like
                # Xlib.error.DisplayConnectionError (no DISPLAY / headless env)
                print(f"Warning: native cursor mode unavailable ({type(e).__name__}: {e}). "
                      f"Falling back to Selenium ActionChains (no visible OS cursor movement).")

    # ---------- helper for safe gaussian sampling ----------

    def _gauss(self, mean, stdev, min_val=None, max_val=None):
        val = random.gauss(mean, stdev)
        if min_val is not None:
            val = max(val, min_val)
        if max_val is not None:
            val = min(val, max_val)
        return val

    # ---------- Core: human-like mouse path generation ----------

    def _bezier_curve(self, start, end, control_points=2, steps=30):
        points = [start]
        for _ in range(control_points):
            t = self._gauss(0.5, 0.15, 0.05, 0.95)
            mid_x = start[0] + (end[0] - start[0]) * t
            mid_y = start[1] + (end[1] - start[1]) * t
            offset_x = self._gauss(0, 20, -60, 60)
            offset_y = self._gauss(0, 20, -60, 60)
            points.append((mid_x + offset_x, mid_y + offset_y))
        points.append(end)

        curve = []
        for t in np.linspace(0, 1, steps):
            x, y = self._bezier_point(points, t)
            curve.append((x, y))
        return curve

    def _bezier_point(self, points, t):
        pts = points[:]
        while len(pts) > 1:
            pts = [
                ((1 - t) * pts[i][0] + t * pts[i + 1][0],
                 (1 - t) * pts[i][1] + t * pts[i + 1][1])
                for i in range(len(pts) - 1)
            ]
        return pts[0]

    def _ease_in_out(self, t):
        return t * t * (3 - 2 * t)

    # ---------- Dynamic timing calculators ----------

    def _dynamic_move_delay(self, distance, steps):
        total_duration = self._gauss(0.15 + distance * 0.0006, 0.05, 0.1, 1.5)
        per_step_mean = total_duration / max(steps, 1)
        return per_step_mean, per_step_mean * 0.3

    def _dynamic_click_delay(self):
        return self._gauss(0.12, 0.05, 0.02, 0.3)

    def _dynamic_hover_time(self, element=None):
        base_mean = 1.2
        if element is not None:
            try:
                area = element.size["width"] * element.size["height"]
                base_mean = min(1.0 + area / 40000, 3.0)
            except Exception:
                pass
        return self._gauss(base_mean, base_mean * 0.3, 0.3, 4.0)

    def _dynamic_typing_delay(self, char=None):
        base_mean = 0.13
        if char in (" ", ",", ".", "!", "?"):
            base_mean += 0.05
        return self._gauss(base_mean, 0.05, 0.03, 0.4)

    def _dynamic_think_pause(self):
        return self._gauss(0.5, 0.15, 0.2, 1.2)

    def _dynamic_scroll_step_delay(self):
        return self._gauss(0.25, 0.08, 0.05, 0.6)

    def _dynamic_scroll_amount(self, remaining):
        return int(self._gauss(120, 35, 30, min(220, max(remaining, 40))))

    def _dynamic_idle_pause(self):
        return self._gauss(0.9, 0.3, 0.2, 2.0)

    def _dynamic_drift_delay(self):
        return self._gauss(0.2, 0.06, 0.05, 0.4)

    # ---------- Scroll position helpers ----------

    def _get_scroll_state(self):
        return self.driver.execute_script(
            "return [document.documentElement.scrollTop || document.body.scrollTop, "
            "document.documentElement.scrollHeight, "
            "document.documentElement.clientHeight];"
        )

    def _can_scroll_down(self):
        scroll_top, scroll_height, client_height = self._get_scroll_state()
        return scroll_top + client_height < scroll_height - 5

    def _can_scroll_up(self):
        scroll_top, _, _ = self._get_scroll_state()
        return scroll_top > 5

    # ---------- Mouse movement ----------

    def _apply_screen_offset(self, browser_x, browser_y):
        win_pos = self.driver.get_window_position()
        toolbar_offset = 85  # approximate; calibrate for your OS/browser/zoom
        return win_pos["x"] + browser_x, win_pos["y"] + toolbar_offset + browser_y

    def move_to_element_like_human(self, element, steps=None, step_delay=None):
        location = element.location_once_scrolled_into_view
        size = element.size
        end_x = location["x"] + size["width"] / 2 + self._gauss(0, 2, -5, 5)
        end_y = location["y"] + size["height"] / 2 + self._gauss(0, 2, -5, 5)

        start = (self.current_x, self.current_y)
        end = (end_x, end_y)
        distance = math.hypot(end_x - start[0], end_y - start[1])

        steps = steps if steps is not None else int(self._gauss(30, 6, 15, 60))
        control_points = int(self._gauss(2, 0.7, 1, 3))
        path = self._bezier_curve(start, end, control_points=control_points, steps=steps)

        if step_delay is None:
            delay_mean, delay_stdev = self._dynamic_move_delay(distance, steps)
        else:
            delay_mean, delay_stdev = step_delay, step_delay * 0.3

        if self.use_native_cursor:
            for i, (x, y) in enumerate(path):
                t = self._ease_in_out(i / max(len(path) - 1, 1))
                jitter_x = self._gauss(0, 0.6, -2, 2)
                jitter_y = self._gauss(0, 0.6, -2, 2)
                sx, sy = self._apply_screen_offset(x + jitter_x, y + jitter_y)
                self.pyautogui.moveTo(sx, sy, duration=0)
                step_time = delay_mean * (1.5 - abs(0.5 - t))
                time.sleep(self._gauss(step_time, delay_stdev, 0.001, None))
            self.current_x, self.current_y = path[-1]
        else:
            actions = ActionChains(self.driver)
            prev_x, prev_y = start
            for i, (x, y) in enumerate(path):
                t = self._ease_in_out(i / max(len(path) - 1, 1))
                jitter_x = self._gauss(0, 0.6, -2, 2)
                jitter_y = self._gauss(0, 0.6, -2, 2)
                dx = (x - prev_x) + jitter_x
                dy = (y - prev_y) + jitter_y
                actions.move_by_offset(dx, dy)
                prev_x, prev_y = x + jitter_x, y + jitter_y
                step_time = delay_mean * (1.5 - abs(0.5 - t))
                time.sleep(self._gauss(step_time, delay_stdev, 0.001, None))
            actions.perform()
            self.current_x, self.current_y = prev_x, prev_y

    # ---------- Public methods ----------

    def simulate_human_behavior(self, num_actions=None):
        num_actions = num_actions if num_actions is not None else int(self._gauss(2, 0.8, 1, 4))
        for _ in range(num_actions):
            action = random.choice([self.scroll_page, self._idle_pause, self._random_drift])
            action()

    def input_search_query(self, query, char_delay=None, think_pause=None, pre_submit_pause=None):
        search_box = self.driver.find_element(By.NAME, "q")
        self.mouse_click(search_box)
        search_box.clear()

        for char in query:
            search_box.send_keys(char)
            delay = char_delay if char_delay is not None else self._dynamic_typing_delay(char)
            time.sleep(delay)
            if random.random() < 0.03:
                pause = think_pause if think_pause is not None else self._dynamic_think_pause()
                time.sleep(pause)

        final_pause = pre_submit_pause if pre_submit_pause is not None else self._gauss(0.6, 0.2, 0.2, 1.5)
        time.sleep(final_pause)
        self.mouse_click(search_box)
        search_box.submit()

    def mouse_click(self, element, click_delay=None):
        self.move_to_element_like_human(element)
        delay = click_delay if click_delay is not None else self._dynamic_click_delay()
        time.sleep(delay)

        if self.use_native_cursor:
            self.pyautogui.click()
        else:
            ActionChains(self.driver).click().perform()

    def mouse_hover(self, element, hover_time=None):
        self.move_to_element_like_human(element)
        duration = hover_time if hover_time is not None else self._dynamic_hover_time(element)
        time.sleep(duration)

    def scroll_page(self, total_scroll=None, step_delay=None, direction=None):
        total_scroll = total_scroll if total_scroll is not None else int(self._gauss(700, 200, 200, 1400))

        current_direction = direction or random.choice(["down", "down", "up"])
        scrolled = 0

        while scrolled < total_scroll:
            can_down = self._can_scroll_down()
            can_up = self._can_scroll_up()

            if not can_down and not can_up:
                break

            if current_direction == "down" and not can_down:
                current_direction = "up"
            elif current_direction == "up" and not can_up:
                current_direction = "down"
            elif random.random() < 0.08:
                flip_to = "up" if current_direction == "down" else "down"
                if (flip_to == "up" and can_up) or (flip_to == "down" and can_down):
                    current_direction = flip_to

            step = self._dynamic_scroll_amount(total_scroll - scrolled)
            signed_step = step if current_direction == "down" else -step

            if self.use_native_cursor:
                self.pyautogui.scroll(-signed_step if current_direction == "down" else abs(signed_step))
            else:
                self.driver.execute_script(f"window.scrollBy(0, {signed_step});")

            scrolled += step
            delay = step_delay if step_delay is not None else self._dynamic_scroll_step_delay()
            time.sleep(delay)

    # ---------- Internal helpers ----------

    def _idle_pause(self, duration=None):
        time.sleep(duration if duration is not None else self._dynamic_idle_pause())

    def _random_drift(self, delay=None):
        dx, dy = self._gauss(0, 10, -25, 25), self._gauss(0, 10, -25, 25)
        if self.use_native_cursor:
            sx, sy = self._apply_screen_offset(self.current_x + dx, self.current_y + dy)
            self.pyautogui.moveTo(sx, sy, duration=0.1)
        else:
            ActionChains(self.driver).move_by_offset(dx, dy).perform()
        self.current_x += dx
        self.current_y += dy
        time.sleep(delay if delay is not None else self._dynamic_drift_delay())