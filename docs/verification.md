# Verification — 27 October 2026

The tested story runs from the rendered website through authenticated Flask POST routes, transactional SQLite changes, and the resulting account and SQL report screens.

## Automated checks

`.venv\Scripts\python.exe -m pytest -q` — **16 passed**.

The 9 database tests cover coherent/idempotent seeding, bid rules and SQL triggers, reserve failure, valid sale creation, sale forgery rejection, immutable history, mandatory references, date/money/junction constraints, concurrent bids and lot closure, atomic opening and rollback after a simulated sale failure.

The 7 web tests cover all public and staff pages, every editable create form, all four dummy logins and role checks, CSRF rejection, form CRUD and constraint feedback, the complete presentation walkthrough, preset report totals, restart persistence and exact money parsing.

## Live browser evidence

- The staff demo button filled the login form, and normal authentication opened the staff desk.
- Sara's account initially showed no bids or purchases.
- Sara submitted a simulated ₹70,000 bid on lot 101 through its rendered form. The auction updated to 3 bids and ₹70,000; the database stored the bid.
- Staff closed the lot through the website. The UI changed to sold and recorded one sale for Sara.
- Staff marked that sale completed through the sale table's payment form. The collector report then displayed Sara spending ₹70,000, Maya ₹55,000, and Arjun ₹0 because his payment remained pending.
- After verification, the local database was explicitly reset to the documented clean fixture and the server restarted with the final code.

## Visual and asset checks

- Desktop and 390×844 mobile layouts were inspected in the browser. The final white-background previews are `work/screenshots/desktop.png` and `work/screenshots/mobile.png`.
- At 390 px, document scroll width equaled viewport width. The staff table independently scrolls within its container.
- Mobile navigation opened correctly. Reduced-motion emulation disabled the hero transform.
- The three rendered objects meet their pedestals; original art is framed and layered in the hero. All hero images loaded in the final mobile browser check.
- All 12 original artwork WebPs were decoded successfully, and the collection browser loaded all 12. All 3 object PNGs retain genuine alpha transparency.

## Final delivered database

- `PRAGMA integrity_check` → `ok`.
- `PRAGMA foreign_key_check` → no violations.
- 17 tables: the 16 domain tables plus `user_account`.
- 25 indexes including primary/unique and explicit relationship/history indexes.
- Clean fixture: 4 accounts, 10 bids and 2 sales; no browser-test purchase left behind.
- Auction 3 is **Recent Acquisitions**, dated at the seed snapshot to match its generated sale records.

This is a local demonstration with simulated bids/payments; no deployment or external payment system was part of verification.

## Interactive frames and presentation studio update

The expanded suite now reports **22 passed**. Six additional presentation tests cover staff-only access, CSRF, allow-listed schema inspection, all eight guided steps, stale/concurrent replay rejection, per-session isolation, restart, failure rollback, and preservation of the main database.

The eight-step guided demo was also run from start to completion through the actual browser. It recorded Maya's ₹65,000 bid and Sara's winning ₹70,000 bid, a single sale, and completed spending of ₹70,000, with actual SQL traces and before/after rows. The main database retained its original 12 artworks, 10 bids and 2 sales.

Interactive frame checks: native dialog opening, manual tilt/rotation, Escape closing and focus return, persisted effects preference, touch behavior, and reduced-motion handling. New controls meet a 44px minimum touch target. Screenshots include `work/screenshots/3d-viewer.png` and `3d-mobile-viewer.png`.

At 390px, the new database explorer's document width and scroll width were both 390px. Its two data tables scroll within 354px containers rather than expanding the page.
