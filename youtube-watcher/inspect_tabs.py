import win32gui
import comtypes.client

def find_browser():
    hwnds = []
    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            for b in ["firefox", "chrome", "edge"]:
                if b in t.lower():
                    hwnds.append((h, t))
                    break
    win32gui.EnumWindows(cb, None)
    return hwnds

browsers = find_browser()
print(f"Found {len(browsers)} browser windows:")
for h, t in browsers:
    print(f"  HWND {h}: {t[:60]}")

if browsers:
    hwnd = browsers[0][0]
    UIAutomationClient = comtypes.client.GetModule("UIAutomationCore.dll")
    uia = comtypes.client.CreateObject(UIAutomationClient.CUIAutomation, interface=UIAutomationClient.IUIAutomation)
    elem = uia.ElementFromHandle(hwnd)
    print("Attached to window element:", elem.CurrentName)
    
    tab_cond = uia.CreatePropertyCondition(UIAutomationClient.UIA_ControlTypePropertyId, UIAutomationClient.UIA_TabItemControlTypeId)
    tabs = elem.FindAll(UIAutomationClient.TreeScope_Descendants, tab_cond)
    print("Tabs found:", tabs.Length)
    for i in range(tabs.Length):
        t = tabs.GetElement(i)
        r = t.CurrentBoundingRectangle
        print(f"Tab {i}: '{t.CurrentName}' -> Left={r.left}, Right={r.right}, Top={r.top}, Bottom={r.bottom}")
        # Search for close button inside the tab
        btn_cond = uia.CreatePropertyCondition(UIAutomationClient.UIA_ControlTypePropertyId, UIAutomationClient.UIA_ButtonControlTypeId)
        btns = t.FindAll(UIAutomationClient.TreeScope_Descendants, btn_cond)
        print(f"   Buttons in tab: {btns.Length}")
        for j in range(btns.Length):
            b = btns.GetElement(j)
            br = b.CurrentBoundingRectangle
            cx = br.left + (br.right - br.left) // 2
            cy = br.top + (br.bottom - br.top) // 2
            print(f"     Button '{b.CurrentName}' -> Center=({cx}, {cy})")
