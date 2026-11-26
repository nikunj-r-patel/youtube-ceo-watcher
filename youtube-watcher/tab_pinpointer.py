from PIL import ImageGrab, Image
import win32gui
import os

def find_youtube_tab_center(hwnd):
    """
    Finds the exact (center_x, center_y) of the YouTube tab's 'X' button.
    1. Tries UIAutomation for native accessibility element.
    2. Uses visual red-logo detection in the tab strip row for pixel-perfection.
    """
    rect = win32gui.GetWindowRect(hwnd)
    win_left, win_top, win_right, win_bottom = rect
    win_w = win_right - win_left
    
    # Method 1: UIAutomation
    try:
        import comtypes.client
        UIAutomationClient = comtypes.client.GetModule("UIAutomationCore.dll")
        uia = comtypes.client.CreateObject(UIAutomationClient.CUIAutomation, interface=UIAutomationClient.IUIAutomation)
        elem = uia.ElementFromHandle(hwnd)
        tab_cond = uia.CreatePropertyCondition(
            UIAutomationClient.UIA_ControlTypePropertyId,
            UIAutomationClient.UIA_TabItemControlTypeId
        )
        tabs = elem.FindAll(UIAutomationClient.TreeScope_Descendants, tab_cond)
        for i in range(tabs.Length):
            t = tabs.GetElement(i)
            name = (t.CurrentName or "").lower()
            if "youtube" in name:
                r = t.CurrentBoundingRectangle
                x_center = r.right - 16
                y_center = r.top + (r.bottom - r.top) // 2
                print(f"🎯 UIAutomation pinpointed 'X' icon: ({x_center}, {y_center})")
                return x_center, y_center
    except Exception:
        pass

    # Method 2: Visual Detection of the YouTube Tab Red Logo in the Tab Strip
    try:
        # Tab strip is located in the top 55 pixels of the browser window
        tab_top = max(0, win_top + 2)
        tab_bottom = tab_top + 48
        strip = ImageGrab.grab(bbox=(win_left, tab_top, win_right, tab_bottom))
        sw, sh = strip.size
        
        red_spots = []
        for x in range(sw):
            for y in range(sh):
                r, g, b = strip.getpixel((x, y))[:3]
                # High red with low green/blue (YouTube Play button red)
                if r > 185 and g < 45 and b < 45:
                    red_spots.append((x, y))
                    
        if red_spots:
            logo_x = int(sum(p[0] for p in red_spots) / len(red_spots))
            logo_y = int(sum(p[1] for p in red_spots) / len(red_spots))
            
            # The 'X' icon is located ~80-95px to the right of the red logo in the same tab
            # Scan rightwards for the bright 'X' icon pixels (near grey/white)
            x_candidates = []
            for scan_x in range(logo_x + 40, min(sw - 10, logo_x + 160)):
                for scan_y in range(max(0, logo_y - 10), min(sh, logo_y + 10)):
                    r, g, b = strip.getpixel((scan_x, scan_y))[:3]
                    if r > 180 and g > 180 and b > 180:
                        x_candidates.append(scan_x)
                        
            if x_candidates:
                best_rel_x = int(sum(x_candidates) / len(x_candidates))
            else:
                best_rel_x = logo_x + 88  # Exact typical offset
                
            exact_screen_x = win_left + best_rel_x
            exact_screen_y = tab_top + logo_y
            print(f"🎯 Visual detection pinpointed 'X' icon at: ({exact_screen_x}, {exact_screen_y})")
            return exact_screen_x, exact_screen_y
    except Exception as e:
        print(f"Visual detection fallback: {e}")

    # Method 3: Calculated fallback
    exact_screen_x = win_left + int(win_w * 0.96)
    exact_screen_y = win_top + 24
    print(f"🎯 Geometry fallback: ({exact_screen_x}, {exact_screen_y})")
    return exact_screen_x, exact_screen_y

if __name__ == "__main__":
    print("Testing tab pinpointer logic...")
