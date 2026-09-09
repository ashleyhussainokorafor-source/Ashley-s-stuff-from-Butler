# How to Point thehcadaily.com to Our Server from Wix

Since **thehcadaily.com** was purchased directly through Wix, you manage its DNS records right inside your Wix account.

---

### Exact Steps in Wix:

1. Go to **[wix.com](https://www.wix.com)** and log in.
2. In the top right, click your profile icon / account menu and go to **Domains** (or visit `manage.wix.com/dashboard/.../domains`).
3. Next to **thehcadaily.com**, click the **More Actions** (three dots `...`) icon.
4. Select **Manage DNS Records**.
5. Look for the **A (Host)** section:
   * Click **Edit** next to the primary A record (pointing to `@`).
   * Change the IP address to:  
     `187.127.64.33`
   * Click **Save**.
6. Look for the **CNAME (Aliases)** section:
   * Ensure `www` points to `thehcadaily.com` (or leave it as is).
   * Click **Save**.

---

*Note: DNS changes take between 15 minutes to a few hours to propagate worldwide.*
