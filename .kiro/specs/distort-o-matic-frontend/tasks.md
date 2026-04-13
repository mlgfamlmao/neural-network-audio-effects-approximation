# Implementation Plan: Distort-o-Matic Frontend

## Overview

Build `api.py` (FastAPI bridge) and `index.html` (single-page glass UI) incrementally. The backend is implemented first so the frontend can be wired to real endpoints. Property-based tests (hypothesis for backend, fast-check for frontend JS) are placed close to the code they validate.

## Tasks

- [x] 1. Set up FastAPI bridge skeleton and project structure
  - Create `api.py` at the project root with FastAPI app, CORS middleware, and imports from `services/agent.py` and `services/files.py`
  - Add `requirements-web.txt` (or extend existing) with `fastapi`, `uvicorn`, `hypothesis`, `pytest`, `httpx`
  - Verify the app starts without errors (`uvicorn api:app`)
  - _Requirements: 3.5_

- [x] 2. Implement `POST /chat` endpoint
  - [x] 2.1 Implement the `/chat` route
    - Accept `{"message": str}`, call `chat.send_message(message)`, return `{"reply": response.text}`
    - Wrap in try/except; return `{"error": str(e)}` with HTTP 500 on failure
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 2.2 Write property test for chat forwarding round-trip (Property 1)
    - **Property 1: Chat forwarding round-trip**
    - Mock `services.agent.chat.send_message`; use `@given(st.text(min_size=1))` to assert reply equals mocked return value
    - **Validates: Requirements 3.2**

  - [ ]* 2.3 Write property test for conversation session preservation (Property 2)
    - **Property 2: Conversation session is preserved**
    - Use `@given(st.lists(st.text(min_size=1), min_size=1, max_size=10))` to send N messages; assert `send_message` called N times on the same mock object
    - **Validates: Requirements 3.3**

- [x] 3. Implement `GET /files` endpoint
  - [x] 3.1 Implement the `/files` route
    - Call `get_files()` from `services/files.py`, return the list as a JSON array
    - _Requirements: 4.1, 4.2_

  - [ ]* 3.2 Write property test for file list pass-through (Property 3)
    - **Property 3: File list pass-through**
    - Mock `services.files.get_files`; use `@given(st.lists(st.text()))` to assert the endpoint returns exactly the mocked list
    - **Validates: Requirements 4.1**

- [x] 4. Implement `GET /download` endpoint
  - [x] 4.1 Implement the `/download` route with path validation
    - Accept `path` query param; resolve against project root; reject paths outside root with HTTP 400; return `FileResponse` with `media_type="audio/wav"`; return HTTP 404 if file not found
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 4.2 Write property test for valid audio file serving (Property 4)
    - **Property 4: Valid audio file is served**
    - Create a temp `.wav` file inside project root; use `@given` path within root; assert 200 and `audio/wav` content-type
    - **Validates: Requirements 5.2**

  - [ ]* 4.3 Write property test for path traversal rejection (Property 5)
    - **Property 5: Path traversal is rejected**
    - Use `@given(st.one_of(st.just("../etc/passwd"), st.text().map(lambda s: "../" + s)))` to assert 400 response and no file content
    - **Validates: Requirements 5.4**

- [x] 5. Implement `GET /outputs/{filename}` endpoint
  - Add route that serves files from `services/outputs/` via `FileResponse`; FastAPI returns default 404 for missing files
  - _Requirements: 2.1_

- [x] 6. Backend checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Build `index.html` — page shell and Glass UI design tokens
  - Create `index.html` with `<style>` block containing CSS custom properties for the glass palette (light pink `#f9c6d0` range, white, blur tokens), base typography (Inter / system-ui), gradient background, and `prefers-color-scheme: dark` overrides
  - Scaffold the three section containers: `#hero`, `#gallery`, `#chatbot`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 8.1, 8.2, 8.3, 8.5_

- [x] 8. Implement Hero section
  - Render project name, description paragraph, and tech-stack badges (PyTorch CNNs, Google Gemini, TinySOL) inside a glass card
  - _Requirements: 1.1, 1.2_

- [x] 9. Implement Model Gallery section
  - [x] 9.1 Render three glass image cards
    - Fetch images from `/outputs/Fuzz.png`, `/outputs/SoftClip.png`, `/outputs/WaveFolding.png`; add effect name label and one-sentence description per card; add `onerror` handler that replaces broken image with a CSS placeholder div
    - _Requirements: 2.1, 2.2, 2.4_

  - [x] 9.2 Add hover transitions
    - Apply CSS `transform: scale(1.03)` and box-shadow glow on `:hover` with `transition` ≤ 300ms
    - _Requirements: 2.3, 8.4_

- [x] 10. Implement Chatbot UI — core messaging
  - [x] 10.1 Build message history, input bar, and send button
    - Render scrollable `#messages` div, `<input id="msg-input">`, and `<button id="send-btn">`; wire Enter key and button click to `sendMessage()`; show user bubble immediately; show loading indicator while fetch is pending; append agent reply on response; scroll to bottom; show inline error bubble on fetch failure
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ]* 10.2 Write property test — user message appears in history (Property 6)
    - **Property 6: User message appears in chat history**
    - Use fast-check `fc.asyncProperty(fc.string({ minLength: 1 }), ...)` with jsdom + mocked fetch; assert user bubble is in DOM before fetch resolves
    - **Validates: Requirements 6.2**

  - [ ]* 10.3 Write property test — agent reply appears in history (Property 7)
    - **Property 7: Agent reply appears in chat history**
    - Use fast-check with mocked `POST /chat` returning arbitrary reply strings; assert reply text appears in `#messages` after fetch resolves
    - **Validates: Requirements 6.4**

- [x] 11. Implement Chatbot UI — audio effect workflow
  - [x] 11.1 Build file selector and selected-file display
    - On page load, `fetch('/files')` and populate `<select id="file-select">` with returned paths; display currently selected filename; include selected path in `POST /chat` message body
    - _Requirements: 7.1, 7.2, 7.4_

  - [ ]* 11.2 Write property test — file selector reflects available files (Property 8)
    - **Property 8: File selector reflects available files**
    - Use fast-check `fc.array(fc.string({ minLength: 1 }))` with mocked `GET /files`; assert `<select>` option count and values match exactly
    - **Validates: Requirements 7.1**

  - [ ]* 11.3 Write property test — selected file included in chat request (Property 9)
    - **Property 9: Selected file is included in chat message context**
    - Use fast-check with arbitrary file path set as selector value; capture fetch body; assert path is present in the request
    - **Validates: Requirements 7.2**

  - [x] 11.4 Detect processed file in agent reply and render download button
    - Parse agent reply for `*_processed.wav` substring; if found, append a download button with `href="/download?path=<extracted_path>"` to the agent message bubble
    - _Requirements: 7.3_

  - [ ]* 11.5 Write property test — processed file triggers download button (Property 10)
    - **Property 10: Processed file triggers download button**
    - Use fast-check `fc.string()` mapped to embed a `_processed.wav` path; assert download button appears with correct href
    - **Validates: Requirements 7.3**

- [x] 12. Apply CSS transitions and animation polish
  - Add `opacity` + `translateY` entrance transitions (≤ 300ms) to message bubbles and send button active state
  - _Requirements: 8.4_

- [x] 13. Frontend checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Wire everything together and final validation
  - [x] 14.1 Confirm `index.html` points to correct API base URL and all four endpoints are reachable
    - Verify `/chat`, `/files`, `/download`, `/outputs/{filename}` all respond correctly when `api.py` is running
    - _Requirements: 3.1, 4.1, 5.1, 2.1_

  - [ ]* 14.2 Write integration tests for end-to-end flows
    - Use `httpx.AsyncClient` with the live FastAPI app (via `TestClient`); test full chat → processed reply → download flow
    - _Requirements: 3.2, 5.2, 7.3_

- [x] 15. Final checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Backend tests: `pytest --hypothesis-seed=0` (min_examples=100)
- Frontend tests: `jest --runInBand` with fast-check numRuns=100
- `api.py` is a thin proxy — all ML logic stays in `services/agent.py`
- The single `chat` session in `api.py` preserves conversation history for the server's lifetime
