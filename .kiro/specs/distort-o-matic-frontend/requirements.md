# Requirements Document

## Introduction

Distort-o-Matic Frontend is a professional web application that showcases an audio distortion ML project. It provides a landing page describing the project, displays neural network model output visualizations, and integrates a chatbot UI connected to the Distort-o-Matic Gemini-powered agent. Users can ask DSP/audio questions and trigger distortion effects on sample audio files through the chat interface. The frontend communicates with a lightweight Python API bridge that proxies messages to the existing `agent.py` chat session.

## Glossary

- **Frontend**: The browser-based web application (HTML/CSS/JS or a lightweight framework).
- **API_Bridge**: A Python HTTP server (e.g. FastAPI or Flask) that exposes REST endpoints consumed by the Frontend and delegates to the Agent.
- **Agent**: The existing `services/agent.py` Gemini-powered chatbot with the `apply_distortion` tool.
- **Chatbot_UI**: The chat interface component rendered in the browser.
- **Model_Gallery**: The section of the page that displays the three neural network output visualization images (Fuzz, SoftClip, WaveFolding).
- **Sample_Audio**: A pre-selected `.wav` file from the TinySOL library or the existing `services/test_audio.wav` used as the default target for distortion effects triggered via chat.
- **Effect**: One of the three distortion types supported by the Agent: `fuzz`, `soft_clip`, or `wave_folding`.
- **Glass_UI**: The visual design language — frosted-glass card components with a light pink color scheme on a soft gradient background.

---

## Requirements

### Requirement 1: Landing Page and Project Description

**User Story:** As a visitor, I want to read a clear description of the Distort-o-Matic project, so that I understand what the application does and the technology behind it.

#### Acceptance Criteria

1. THE Frontend SHALL render a hero section containing the project name "Distort-o-Matic", a one-paragraph description of the project, and the technology stack (PyTorch CNNs, Google Gemini, TinySOL).
2. THE Frontend SHALL apply the Glass_UI design language: frosted-glass card surfaces, a light pink and soft white color palette, and a subtle gradient background.
3. THE Frontend SHALL be responsive and render correctly on viewport widths from 375px to 1440px.
4. WHEN the page loads, THE Frontend SHALL display all primary sections (hero, Model_Gallery, Chatbot_UI) without requiring user interaction.

---

### Requirement 2: Model Output Gallery

**User Story:** As a visitor, I want to see the neural network model output visualizations, so that I can understand what each distortion effect does to an audio signal.

#### Acceptance Criteria

1. THE Model_Gallery SHALL display three images: `Fuzz.png`, `SoftClip.png`, and `WaveFolding.png` served from `services/outputs/`.
2. THE Model_Gallery SHALL label each image with the corresponding effect name and a one-sentence description of the effect's sonic character.
3. WHEN an image is hovered, THE Model_Gallery SHALL apply a subtle scale or glow transition to indicate interactivity.
4. IF an image fails to load, THEN THE Model_Gallery SHALL display a placeholder with the effect name in place of the broken image.

---

### Requirement 3: API Bridge — Chat Endpoint

**User Story:** As a developer, I want a backend API endpoint that proxies chat messages to the Agent, so that the Frontend can communicate with the Gemini-powered chatbot without exposing API keys to the browser.

#### Acceptance Criteria

1. THE API_Bridge SHALL expose a `POST /chat` endpoint that accepts a JSON body with a `message` string field.
2. WHEN a valid request is received, THE API_Bridge SHALL forward the `message` to the Agent's `chat.send_message()` method and return the Agent's text response as JSON with a `reply` string field.
3. THE API_Bridge SHALL preserve the Agent's conversation history across multiple requests within the same server session.
4. IF the Agent raises an exception, THEN THE API_Bridge SHALL return a JSON error response with an `error` field and an HTTP 500 status code.
5. THE API_Bridge SHALL include CORS headers permitting requests from the Frontend's origin.

---

### Requirement 4: API Bridge — Audio File Endpoint

**User Story:** As a developer, I want the API bridge to serve available audio files, so that the Frontend can display selectable sample files for distortion.

#### Acceptance Criteria

1. THE API_Bridge SHALL expose a `GET /files` endpoint that returns a JSON array of available `.wav` file paths from the TinySOL library using the existing `services/files.py` `get_files()` function.
2. WHEN the `/files` endpoint is called, THE API_Bridge SHALL return paths relative to the project root.

---

### Requirement 5: API Bridge — Processed Audio Download

**User Story:** As a user, I want to download the processed audio file after the Agent applies a distortion effect, so that I can listen to the result.

#### Acceptance Criteria

1. THE API_Bridge SHALL expose a `GET /download` endpoint that accepts a `path` query parameter specifying a processed `.wav` file path.
2. WHEN a valid processed file path is provided, THE API_Bridge SHALL return the file as an audio/wav binary response.
3. IF the requested file does not exist, THEN THE API_Bridge SHALL return a JSON error response with an HTTP 404 status code.
4. THE API_Bridge SHALL restrict downloadable paths to files within the project directory to prevent path traversal.

---

### Requirement 6: Chatbot UI — Messaging

**User Story:** As a user, I want to send messages to Distort-o-Matic and receive responses in a chat interface, so that I can ask DSP questions and trigger audio effects conversationally.

#### Acceptance Criteria

1. THE Chatbot_UI SHALL render a scrollable message history area and a text input field with a send button.
2. WHEN the user submits a message, THE Chatbot_UI SHALL display the user's message immediately in the history and send it to the `POST /chat` endpoint.
3. WHILE a response is pending, THE Chatbot_UI SHALL display a loading indicator in the message history.
4. WHEN a response is received, THE Chatbot_UI SHALL display the Agent's reply in the message history and scroll to the latest message.
5. IF the API call fails, THEN THE Chatbot_UI SHALL display an inline error message in the chat history without clearing the conversation.
6. THE Chatbot_UI SHALL allow message submission via the Enter key as well as the send button.

---

### Requirement 7: Chatbot UI — Audio Effect Workflow

**User Story:** As a user, I want to trigger a distortion effect on a sample audio file through the chat and then download the result, so that I can hear the neural network's output.

#### Acceptance Criteria

1. THE Chatbot_UI SHALL display a sample file selector that lists available `.wav` files fetched from `GET /files`, allowing the user to choose which file the Agent will process.
2. WHEN the user selects a file, THE Chatbot_UI SHALL include the selected file path in the context available to the Agent (e.g. pre-populated in the message or sent as metadata).
3. WHEN the Agent's reply indicates a file was successfully processed (contains a file path ending in `_processed.wav`), THE Chatbot_UI SHALL render a download button linking to `GET /download?path=<processed_path>`.
4. THE Chatbot_UI SHALL display the name of the currently selected sample file so the user knows which file will be processed.

---

### Requirement 8: Professional Visual Design

**User Story:** As a visitor, I want the application to look polished and modern, so that the project is presented credibly.

#### Acceptance Criteria

1. THE Frontend SHALL use a consistent type scale with a sans-serif font (e.g. Inter or system-ui) across all sections.
2. THE Frontend SHALL apply Glass_UI styling to all card components: `backdrop-filter: blur`, semi-transparent backgrounds, and soft border highlights.
3. THE Frontend SHALL use a primary color palette of light pink (`#f9c6d0` range) and white/off-white, with dark text for readability meeting a minimum contrast ratio of 4.5:1 for body text.
4. THE Frontend SHALL animate the chat send button and message bubbles with subtle CSS transitions (opacity and translate) of no more than 300ms duration.
5. WHERE a dark-mode preference is detected via `prefers-color-scheme: dark`, THE Frontend SHALL apply an alternative dark glass palette while preserving the pink accent color.
