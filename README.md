# 🍍 Pineapple Arcade

50,000+ browser games in one place (original 895 plus the GameDistribution and GameMonetize catalogs). Forgiving search (typos, no spaces, initials like "fnf"), categories, favorites, continue-playing, and play time. Game saves persist per device; use Backup/Restore to move favorites and history.

Play: https://burntpineapples.github.io/pineapple-arcade/

Test the search: `node test-search.js`

## Daily stats
Anonymous visit and play counts go to GoatCounter (`pineapplearcade.goatcounter.com`). `.github/workflows/daily-stats.yml` posts yesterday's summary to the `WEBHOOK_URL` secret every morning; it also needs a `GOATCOUNTER_TOKEN` secret.
