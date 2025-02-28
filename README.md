#

# Pfusch
Der komplette Login für 1Komma5Grad is Pfusch, da die OAuth Schnittstelle nicht Dokumentiert ist und die Redirect_url nicht änderbar ist muss der Login in einem neuen Tab mit Browser Konsole und Custom Registry Key abgefangen werden.

## 1. Installation
Für die Installation der Integration muss das Repository nach custom_components gecloned werden.
```
mkdir custom_components && cd custom_components
git clone https://github.com/domenik1023/1komma5

reboot
```

## 2. Setup
### Registry
Um die Integration Nutzen zu können muss in der Windows Registry der ein custom handler angelegt werden.

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\io.onecommafive.my.production.app]
@="URL:Heartbeat OAuth"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\io.onecommafive.my.production.app\shell]

[HKEY_CLASSES_ROOT\io.onecommafive.my.production.app\shell\open]

[HKEY_CLASSES_ROOT\io.onecommafive.my.production.app\shell\open\command]
@="\"C:\\Path\\to\\python.exe\" \"C:\\Path\\to\\your_script.py\" \"%1\""
```

### Home Assistant
Nach der Installation und der Einstellung in der Windows Registry kann nun die Konfiguration in Home Assistant erfolgen.
Dafür kann unter Settings -> Devices & Services -> Add Integration -> 1Komma5Grad die integration hinzugefügt werden.

Als erstes wird ein Authorization Code abgefragt. Dieser kann durch die URL in Notifications generiert werden.
Am besten dafür einfach ein neues Fenster mit Home Assistant öffen. (Ich weiß das das blöd ist lol)

Nach dem öffnen der Login Seite für 1Komma5Grad sollte im Browser die Konsole (Chromium: F12) geöffnet werden. Nach dem Login sollte das "Open URL" Popup erscheinen dort auf Open URL Klicken. In der Konsole sollte jetzt folgendes stehen: `Launched external handler for io.onecommafive.my.production.app://auth.1komma5grad.com/android/io.onecommafive.my.production.app/callback?code=HIER_DER_CODE&state=01JN6MXDHVK1DC5V0033QNY1WQ`

Hier muss der Code Kopiert und in Home Assistant eingefügt werden.

Nach dem Einfügen des Codes werden Alle Systeme Geladen, hier kann sich Zwischen dem Demo System und dem eigenen Endschieden werden.

Unter Configuration lässt sich das System ändern und ein Force Refresh des Tokens erziehlen.

### 3. Configuration
Es lassen sich noch IntegrationSensors für die Energy Map von Home Assistant erstellen.

dafür muss in der configuration.yml folgendes hinzugefügt werden.

```yml
sensor:
    - platform: integration
    source: sensor.solar_production
    name: Total Solar Production
    unique_id: 1k5_total_solar_production
    unit_prefix: k
    round: 4

    - platform: integration
    source: sensor.consumption
    name: Total House Consumption
    unique_id: 1k5_total_house_consumption
    unit_prefix: k
    round: 4

    - platform: integration
    source: sensor.grid_consumption
    name: Total Grid Consumption
    unique_id: 1k5_total_grid_consumption
    unit_prefix: k
    round: 4

    - platform: integration
    source: sensor.grid_feed_in
    name: Total Grid Feed In
    unique_id: 1k5_total_grid_feedin
    unit_prefix: k
    round: 4

    - platform: integration
    source: sensor.battery_power
    name: Total Battery
    unique_id: 1k5_total_battery
    unit_prefix: k
    round: 4

    - platform: integration
    source: sensor.battery_power_in
    name: Total Battery In
    unique_id: 1k5_total_battery_in
    unit_prefix: k
    round: 4

    - platform: integration
    source: sensor.battery_power_out
    name: Total Battery Out
    unique_id: 1k5_total_battery_out
    unit_prefix: k
    round: 4
```