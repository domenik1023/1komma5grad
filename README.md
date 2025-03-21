# 1Komma5Grad Home Assistant Integration (Unofficial)

**Disclaimer** :

This integration provides access to 1Komma5Grad systems despite the lack of official OAuth documentation. The OAuth flow is somewhat hacky due to the inability to configure the redirect URI, and it requires a custom URL handler to intercept the login callback.

---

## 🚀 Features

- Integration with Home Assistant

- Support for Home Assistant's Energy dashboard

- Sensors for solar production, consumption, grid interaction and battery usage

---

## 📦 Installation

Prerequisite: [HACS](https://hacs.xyz/) (Home Assistant Community Store)

This integration requires HACS to be installed and configured in your Home Assistant instance.

### Installation via HACS

2. Open Home Assistant and go to **HACS → Integrations** .

3. Click on the **three dots (⋮)** in the top right and select **Custom Repositories** .

4. Add this repository:

```arduino
https://github.com/domenik1023/1komma5grad
```

- **Category** : Integration

8. After adding, search for **1Komma5Grad** in the HACS integration list and install it.

9. Restart Home Assistant once the installation is complete.

---

## ⚙️ Setup Instructions

### 1. Home Assistant Configuration

Once the Integration is installed.

1. Navigate to **Settings → Devices & Services → Add Integration**.

2. Search for and add **1Komma5Grad**.

#### OAuth Login

- A popup will request an **Authorization Code**.

- Open a **new tab** with Home Assistant running and trigger the login flow.

- In the login window for 1Komma5Grad:

  - Open the browser developer console (usually `F12` on Chromium).

In the browser console, you'll see a log like:

```bash
Failed to launch 'io.onecommafive.my.production.app://auth.1komma5grad.com/android/io.onecommafive.my.production.app/callback?code={HERE_WILL_BE_YOUR_CODE&state=01JPWQX64RJ8DC869S0E6C6VK2' because the scheme does not have a registered handler.
```

Copy the `code` parameter from this URL and paste it into Home Assistant.

---

## 🧩 Configuration

### System Selection

If everything is set up correctly, you should now see at least two available system IDs.

Choose the **System ID** that corresponds to your setup.

Once selected, you’ll be prompted to add the available sensors.

### Optional Configuration

You can optionally add [integration sensors]() for the Home Assistant Energy dashboard by updating your `configuration.yaml`:

```yaml
sensor:
  - platform: integration
    source: sensor.1k5_solar_production
    name: Total Solar Production
    unique_id: 1k5_total_solar_production
    unit_prefix: k
    round: 1

  - platform: integration
    source: sensor.1k5_house_consumption
    name: Total House Consumption
    unique_id: 1k5_total_house_consumption
    unit_prefix: k
    round: 4

  - platform: integration
    source: sensor.1k5_grid_consumption
    name: Total Grid Consumption
    unique_id: 1k5_total_grid_consumption
    unit_prefix: k
    round: 4

  - platform: integration
    source: sensor.1k5_grid_feed_in
    name: Total Grid Feed In
    unique_id: 1k5_total_grid_feedin
    unit_prefix: k
    round: 4

  - platform: integration
    source: sensor.1k5_battery_energy
    name: Total Battery
    unique_id: 1k5_total_battery
    unit_prefix: k
    round: 4

  - platform: integration
    source: sensor.1k5_battery_in
    name: Total Battery In
    unique_id: 1k5_total_battery_in
    unit_prefix: k
    round: 4

  - platform: integration
    source: sensor.1k5_battery_out
    name: Total Battery Out
    unique_id: 1k5_total_battery_out
    unit_prefix: k
    round: 4
```

---

## ⚠️ Notes

- The login process is a workaround and might break if the OAuth flow changes.
- This project is not affiliated with or endorsed by 1Komma5Grad.
- This project was mostly written with the help of ChatGPT and might not be perfect.
- I will not provide any Support for this integration.
- If you can Improve this integration, please open a PR or issue.

---
