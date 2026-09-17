# Family sync — deployment and remaining activation

GitHub Pages serves the public trip guide. Personal documents, expenses and shared progress require both a confirmed Supabase email and an explicit allowlist entry, plus trip membership. A join code alone cannot grant access.

The migration `secure_family_access_and_private_tickets` was applied through Supabase MCP on 2026-09-17. The earlier five-table schema was already applied manually. Do not blindly run `db push` against this project without first reconciling that baseline.

## Activate approved accounts

Obtain the exact email addresses from Omree and Liat. Add them to `tatry_private.allowed_emails` through the trusted Supabase SQL Editor, using parameterized SQL or properly quoted values. Set `can_create=true` only for Omree. Never commit their addresses to this public repository. Anyone else remains denied even if they sign in or know the trip code.

In Supabase Authentication → URL Configuration, add `https://ok-bar.github.io/tatry-family-2027/` to Redirect URLs. Preserve the existing Site URL if this project also serves another app. This frontend passes the full Pages URL as `emailRedirectTo`.

Confirm email delivery is configured. Supabase's default mail service may restrict delivery to project team addresses; production access for both people can require a custom SMTP provider. No real email was sent during testing.

After activation: Omree signs in and creates the trip; Liat signs in and joins using the code. On the original device, use “העברת הנתונים הישנים ממכשיר זה” to import old local records/documents explicitly. Existing legacy data is not silently uploaded or erased.

## Data behavior

Each browser/account/trip uses a separate IndexedDB database. Local edits and the upload outbox are committed atomically. Different entities merge independently. For the same entity, the last write reaching the server wins. Deletions use tombstone rows so other devices remove the item. Files use authenticated private-bucket downloads, never public or signed bearer URLs.

Reconnection retries pending changes. A fresh private-session unlock requires an online approval check; public itinerary pages remain available offline after preparing the site. Files explicitly downloaded to the user's device remain under their control. Signing out clears the current private database on this browser after warning if unsynced edits exist. The older pre-sync local database is preserved for manual migration.

## Verification

`tests/sync.cjs` exercises two isolated device databases with a mocked server: expenses, offline merge, zero budget, checklists, deletions, retries, transaction rollback, file upload/download and logout. It uses fake-indexeddb 6.2.4 and linkedom 0.18.12.

Live database RLS was tested in a rolled-back transaction: allowed owner/member access, unauthorized user denied even with the code, revoked member denied, cross-trip row reassignment denied, and private file policy checks. Live end-to-end email authentication requires the two real addresses and email configuration.

## Map

The map view and day filter are implemented. Only verified coordinates are drawn. Completing geocoding is paused because automatic review requires user consent to send destination names to Nominatim. No itinerary geocoding batch ran. Tile background loads only when requested and is not bulk-cached.
