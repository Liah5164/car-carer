# API Reference

Car Carer exposes a REST API at `http://localhost:8200/api/`.

Interactive documentation: http://localhost:8200/docs (Swagger UI)

## Authentication

- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Login (sets cookie)
- `POST /api/auth/logout` — Logout
- `GET /api/auth/me` — Current user info
- `POST /api/auth/change-password` — Change password

## Vehicles

- `GET /api/vehicles` — List vehicles
- `POST /api/vehicles` — Create vehicle
- `GET /api/vehicles/{id}` — Get vehicle
- `PATCH /api/vehicles/{id}` — Update vehicle
- `DELETE /api/vehicles/{id}` — Delete vehicle
- `GET /api/vehicles/dashboard` — Dashboard stats
- `GET /api/vehicles/{id}/analysis` — AI analysis
- `GET /api/vehicles/{id}/stats` — Charts data

## Documents

- `POST /api/documents/upload` — Upload + extract
- `POST /api/documents/batch-upload` — Batch upload
- `GET /api/documents/batch-status/{id}` — SSE progress

## Fuel

- `POST /api/vehicles/{id}/fuel` — Add fuel record
- `GET /api/vehicles/{id}/fuel` — List fuel records
- `GET /api/vehicles/{id}/fuel/stats` — Consumption stats
- `DELETE /api/vehicles/{id}/fuel/{fid}` — Delete

## Tax & Insurance

- `POST /api/vehicles/{id}/tax-insurance` — Add record
- `GET /api/vehicles/{id}/tax-insurance` — List
- `PATCH /api/vehicles/{id}/tax-insurance/{rid}` — Update
- `DELETE /api/vehicles/{id}/tax-insurance/{rid}` — Delete

## Notes

- `POST /api/vehicles/{id}/notes` — Add note
- `GET /api/vehicles/{id}/notes` — List (search with ?q=)
- `PATCH /api/vehicles/{id}/notes/{nid}` — Update
- `DELETE /api/vehicles/{id}/notes/{nid}` — Delete

## Sharing

- `POST /api/vehicles/{id}/share` — Share vehicle
- `GET /api/vehicles/{id}/access` — List access
- `DELETE /api/vehicles/{id}/access/{aid}` — Revoke
- `GET /api/vehicles/shared-with-me` — Shared with me

## Chat

- `POST /api/chat` — Send message
- `GET /api/chat/conversations` — List conversations
- `GET /api/chat/conversations/{id}/messages` — Get messages
- `DELETE /api/chat/conversations/{id}` — Delete conversation
