Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement
$browserClasses = @('MozillaWindowClass', 'Chrome_WidgetWin_1')

foreach ($cls in $browserClasses) {
    $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ClassNameProperty, $cls)
    $wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
    foreach ($win in $wins) {
        $name = $win.Current.Name
        if ($name -like '*YouTube*') {
            Write-Host "Found Window: $name"
            $tabCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::TabItem)
            $tabs = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $tabCond)
            foreach ($t in $tabs) {
                $r = $t.Current.BoundingRectangle
                Write-Host "Tab: $($t.Current.Name) Rect: $($r.X), $($r.Y), $($r.Width), $($r.Height)"
            }
        }
    }
}
