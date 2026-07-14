# Highway Pilot App Store Launch Guide

This project is now prepared for multi-store distribution with:
- Web/PWA branding + manifest
- Capacitor mobile wrapper for Android and iOS
- Store-ready logo assets

## Brand Assets Included

- [pilot-web/public/logo-mark.svg](pilot-web/public/logo-mark.svg) : Primary app icon/logo mark
- [pilot-web/public/brand-banner.svg](pilot-web/public/brand-banner.svg) : Marketing/banner image
- [pilot-web/public/manifest.webmanifest](pilot-web/public/manifest.webmanifest) : PWA metadata

## 1) Build Web App

From [pilot-web](pilot-web):

```bash
npm install
npm run build
```

## 2) Generate Native Projects (Capacitor)

From [pilot-web](pilot-web):

```bash
npm run cap:add:android
npm run cap:add:ios
npm run cap:sync
```

## 3) Android (Google Play)

1. Open Android Studio:
```bash
npm run cap:android
```
2. Set package id `com.highwaypilot.app` if needed.
3. Create signed AAB (Build > Generate Signed Bundle).
4. Upload to Google Play Console.
5. Complete store listing with screenshots, privacy policy, and content rating.

## 4) iOS (Apple App Store)

1. Open Xcode:
```bash
npm run cap:ios
```
2. Set bundle identifier (match App Store Connect app).
3. Configure signing/team profile.
4. Archive and upload to App Store Connect.
5. Complete TestFlight + production listing.

## 5) Microsoft Store (Windows)

Fastest path: publish PWA package.

1. Deploy web app (already ready for Vercel/Render).
2. Use PWA Builder (https://www.pwabuilder.com) with your public URL.
3. Generate Microsoft Store package and submit via Partner Center.

## 6) Required Accounts

- Google Play Console (one-time fee)
- Apple Developer Program (annual fee)
- Microsoft Partner Center

## 7) Required Store Metadata

Prepare before submission:
- App name: Highway Pilot
- Short description + full description
- Privacy policy URL
- Support URL
- Screenshots (phone + tablet)
- Feature graphic/banner (use [pilot-web/public/brand-banner.svg](pilot-web/public/brand-banner.svg) as source)

## 8) Production API

For mobile and web store builds, set:

- `VITE_API_BASE_URL` to your public backend URL

Example:

```bash
VITE_API_BASE_URL=https://your-api-domain.com
```

## 9) Recommended Next Enhancements

- Generate PNG icon set (1024, 512, 192, 180, 144)
- Add splash screens per platform
- Add in-app update checks
- Add mobile push notifications
- Add offline caching strategy for PWA

## Notes

Store publication itself cannot be fully automated from code alone because each store requires account verification, legal declarations, and manual review submission.
