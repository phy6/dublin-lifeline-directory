# Dublin City Support Services

A Progressive Web App (PWA) that helps Dublin City residents find nearby support services.

## Features

- **Service Directory**: Search and browse 14+ Dublin support services by category
- **Interactive Map**: Leaflet.js map with OpenStreetMap tiles showing all locations
- **Offline Support**: Service Worker + Cache API for offline access
- **PWA Install**: Scan QR code on flyers → "Add to Home Screen"
- **Auto-Updates**: GitHub Actions runs the Python 3 scraper daily
- **Provider Forms**: Web3Forms integration for future provider submissions

## Quick Start

```bash
npm install
npm run dev
```

## Deployment

Hosted on GitHub Pages. The scraper runs daily via GitHub Actions.

## Tech Stack

- **Framework**: SvelteKit
- **PWA**: @vite-pwa/sveltekit
- **Map**: Leaflet.js + OpenStreetMap
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions
- **Forms**: Web3Forms
- **Scraper**: Python 3

## License

MIT
