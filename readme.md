# WhatsApp Desktop Enhancer

**Author:** mrido1

This add-on is a specialized accessibility bridge for the **modern WhatsApp Desktop application** (available from the Microsoft Store). It enhances navigation efficiency and fixes interaction issues caused by the application's underlying technology.

<div class="info-box">

### Why is this add-on needed?

WhatsApp has gone through several technological shifts on Windows, creating confusion regarding accessibility:

*   **Native UWP Era (The Golden Age):** Starting as a Beta in **November 2021** and releasing globally in **August 2022**, this native version was the pinnacle of accessibility on Windows. It offered lightning-fast performance and perfect screen reader support.
*   **WebView2 Era (The Regression):** The shift began with a Beta in **July 2025**, and was forced onto stable users between **November and December 2025**. This update replaced the native engine with a web-hybrid (WebView2), causing significant accessibility issues (like focus instability and Browse Mode conflicts) that this add-on aims to fix.

**The Problem:** The current version often confuses screen readers. NVDA may try to treat it as a webpage (activating Browse Mode), which breaks standard keyboard shortcuts like `Ctrl+F` or typing. Focus can also get "stuck" in list items.

**The Solution:** This add-on forces NVDA to treat WhatsApp like a standard desktop application by **automatically disabling Browse Mode**. It also adds custom tools to inspect messages that are otherwise hard to reach.

</div>

## Native Shortcuts (Highly Recommended)

Because the modern WhatsApp app is designed to be navigated with a keyboard, you should prioritize these built-in shortcuts. They are faster and more reliable than any add-on script.

### Chat Management

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + Shift + U` | Mark as unread |
| `Ctrl + Shift + M` | Mute |
| `Ctrl + Shift + A` | Archive chat |
| `Ctrl + Alt + Shift + P` | Pin chat |
| `Ctrl + ]` | Next Chat |
| `Ctrl + [` | Previous Chat |
| `Ctrl + Shift + N` | New Group |
| `Ctrl + Alt + N` | New Chat |
| `Escape` | Close Chat |
| `Ctrl + Shift + B` | Block Chat |
| `Ctrl + Alt + Shift + L` | Label chat (Business) |

### Message & Navigation

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + Alt + /` | Search |
| `Ctrl + Shift + F` | Search in Chat |
| `Alt + K` | Extended Search |
| `Ctrl + Alt + P` | Profile and About |
| `Alt + I` | Open Chat Info |
| `Alt + S` | Settings |
| `Alt + L` | Lock App |
| `Ctrl + 1..9` | Open Chat (by position) |

### Message Actions

| Shortcut | Action |
| :--- | :--- |
| `Alt + R` | Reply |
| `Ctrl + Alt + R` | Reply Privately |
| `Ctrl + Alt + D` | Forward |
| `Alt + 8` | Star Message |
| `Ctrl + Arrow Up` | Edit Last Message |
| `Alt + A` | Open Attachment Panel |
| `Ctrl + Alt + E` | Emoji Panel |
| `Ctrl + Alt + G` | GIF Panel |
| `Ctrl + Alt + S` | Sticker Panel |

### Voice Messages (PTT)

| Shortcut | Action |
| :--- | :--- |
| `Shift + .` | Increase Playback Speed |
| `Shift + ,` | Decrease Playback Speed |
| `Ctrl + Enter` | Send PTT |
| `Alt + P` | Pause PTT Recording |
| `Ctrl + Alt + Shift + R` | Star PTT Recording |

### Zoom Control

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + +` | Zoom In |
| `Ctrl + -` | Zoom Out |
| `Ctrl + 0` | Reset Zoom |

## Add-on Features

These features supplement the native experience, filling gaps where accessibility is still lacking.

### 1. Enhanced Message Reading

Sometimes, focusing on a long message in the list is difficult, or NVDA reads it too quickly.

| Shortcut | Action |
| :--- | :--- |
| `Alt + C` | **Text Window View:** Opens the currently focused message in a separate, dedicated text window. You can use standard arrow keys to read line-by-line or select text to copy. Press `Escape` to close. |
| `Control + C` | **Quick Copy:** Copies the text of the focused message bubble directly to the clipboard. |

### 2. Last Spoken Text Review

Since this add-on **disables Browse Mode by default** to ensure smooth navigation, NVDA's standard review cursor (which typically relies on the virtual buffer in web content) may not function as expected for reviewing fleeting announcements or toast notifications.

To overcome this limitation, this add-on includes a custom review feature that captures the last thing NVDA spoke, allowing you to check details you might have missed.

| Shortcut | Action |
| :--- | :--- |
| `NVDA + Left/Right Arrow` | Review the last spoken text **character by character**. |
| `NVDA + Ctrl + Left/Right Arrow` | Review the last spoken text **word by word**. |

### 3. Smart Phone Number Filtering

WhatsApp chat headers often contain a long list of unsaved phone numbers (e.g., in group chats), which can be verbose and distracting when read aloud.

This add-on includes a **smart filter** that automatically removes these numbers from speech while preserving important context (like contact names or notification details). The filter is intelligent enough to distinguish between a list of contacts (where numbers should be read) and a chat header (where they are redundant).

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + Shift + E` | **Toggle Filter:** Instantly enables or disables the phone number filter. You can also configure this preference permanently in the add-on settings. |

### 4. Smart Usage Hints Filtering

When navigating the chat list, WhatsApp often appends repetitive instructions to every item, such as *"For more options, press left or right arrow key to access context menu"* or its translated equivalents. Hearing this on every single chat can be extremely tiresome and slows down navigation significantly.

This add-on automatically detects and **silences these usage hints**, allowing you to hear only the relevant information (Chat Name, Message Preview, Time, and Status).

*   **How it works:** The filter intelligently separates the chat content from the metadata (timestamp) and removes the long instruction text that follows, while preserving important status updates like *"has reaction"* or *"unread"*.
*   **Configuration:** This feature is disabled by default. If you prefer to not  hearing these hints, you can unchecked "Read usage hints while navigating chat list" in the add-on settings panel.

## Contributions

If you have suggestions, feature requests, or would like to report a bug, please feel free to contribute:

*   **Email:** [bredgreene5@gmail.com](mailto:bredgreene5@gmail.com)
*   **GitHub:** You can open an issue or submit a Pull Request on the project repository.
