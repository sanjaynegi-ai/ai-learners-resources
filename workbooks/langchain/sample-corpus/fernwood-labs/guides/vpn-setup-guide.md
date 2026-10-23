# VPN Setup Guide

**Audience:** All employees with remote access needs.

## Steps

1. Install the **WireGuard** client for your operating system from wireguard.com.
2. Log in to `portal.fernwoodlabs.example/vpn` with your Okta credentials.
3. Download your personal `.conf` profile from the portal.
4. Import the profile into the WireGuard client ("Add Tunnel" → "Import from file").
5. Click **Activate** to connect.

## Split Tunneling

Split tunneling is **enabled by default**. Only traffic to `*.fernwoodlabs.example` domains is routed through the VPN; all other internet traffic uses your local connection directly. This is intentional — it keeps your personal browsing off the corporate network and reduces VPN load.

## Troubleshooting

- If the tunnel shows "Active" but internal sites don't load, check that your laptop clock is synced (WireGuard handshakes fail with clock drift over 2 minutes).
- VPN profiles expire after 180 days and must be re-downloaded from the portal.
- For persistent issues, open a ticket in the `#it-help` Slack channel or file a Jira ticket under the `ITOPS` project.
