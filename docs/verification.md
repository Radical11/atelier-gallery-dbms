# Historical SQLite verification

This document predates the Oracle migration. Current Oracle evidence is in `docs/assignment/`; do not interpret earlier SQLite results as verification of the running backend.

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

## Inline dimensional artwork update

The separate inspection buttons and modal viewer have been removed. The frames now interact directly inside the normal gallery, auction and artwork pages. Four actual side planes connect to a raised front face and mat. The frame assembly retains `transform-style: preserve-3d` with `filter: none`; shadows are applied outside that assembly so they do not flatten the geometry.

Browser checks verified a visible projected side edge, cursor tilt, direct artwork dragging, arrow-key rotation and Home reset. Ordinary artwork links continue to navigate. The gallery camera responds to pointer movement and its paintings and foreground objects occupy distinct depth planes. Mobile and reduced-motion modes disable automatic camera movement; manual detail controls remain available.

The 390px layout had no horizontal page overflow, and no inspector buttons or dialog remained in the DOM. The 22-test application suite passed after the template changes. Current previews: `work/screenshots/inline-3d-home.png`, `inline-3d-detail.png`, `inline-3d-side.png` and `inline-3d-mobile.png`.

## Grab-and-drag movement correction

The homepage scene container intercepted pointer hits on its paintings. The container now ignores pointer hits while its movable children receive them explicitly. Paintings and sculptures now support actual position changes, rather than only hover tilt. Collection frames are movable as well. Dragging suppresses the artwork link only for that drag; ordinary clicks retain navigation. Reset controls and keyboard movement are available.

Actual browser mouse drags moved the first painting −70/−40 pixels, the second −70/+40 pixels, and the bust +40/−35 pixels without navigating away. Reset restored all scene positions; a keyboard arrow moved the bust 12 pixels; clicking a painting opened its normal record. On the detail page, a vertical mouse drag moved the frame 50 pixels, arrow-key rotation changed its angle, and Reset frame cleared both values. The web suite passed all 7 tests and both JavaScript files passed syntax checks.

Responsive check: at 390px, page width and scroll width matched. Real touch-event injection was unavailable in the in-app test browser; touch interaction is therefore not claimed as physically verified. All temporary browser emulation overrides were cleared.
