# WhatsApp Desktop Enhancer

**Author:** mrido1

WhatsApp Desktop Enhancer is a specialized accessibility bridge designed for the **modern WhatsApp Desktop application** (available via the Microsoft Store). This add-on streamlines navigation and resolves critical interaction issues introduced by recent changes in WhatsApp's underlying technology.

> [!NOTE]
> ### Why is this add-on necessary?
>
> The Windows version of WhatsApp has undergone several major architectural shifts, leading to significant accessibility challenges:
>
> *   **The Native Era (UWP):** Between **2021 and 2022**, WhatsApp released a native UWP version that offered exceptional performance and seamless screen reader support. It was widely considered the "gold standard" for accessibility.
> *   **The WebView2 Era:** Starting in **late 2025**, WhatsApp transitioned to a web-hybrid engine (WebView2). While this allowed for easier cross-platform updates, it introduced severe regressions for screen reader users, including focus instability and disruptive "Browse Mode" conflicts.
>
> **The Problem:** Because the new app is web-based, NVDA often incorrectly activates "Browse Mode." This interferes with standard keyboard shortcuts (like `Ctrl+F`) and makes typing difficult. Furthermore, focus frequently becomes "stuck" within list items.
>
> **The Solution:** This add-on optimizes the experience by **automatically disabling and locking Browse Mode**, forcing NVDA to treat WhatsApp as a standard desktop application. While this lock is active by default to ensure stability, advanced users can opt to disable it in the settings (though this is generally not recommended).

## Built-in Native Shortcuts (Highly Recommended)

Since the modern WhatsApp app is built for keyboard-centric navigation, we strongly recommend prioritizing these native shortcuts. They are inherently faster and more reliable than any third-party script.

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

### Navigation & Search

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + Alt + /` | Global Search |
| `Ctrl + Shift + F` | Search within current chat |
| `Alt + K` | Extended Search |
| `Ctrl + Alt + P` | Profile & About |
| `Alt + I` | Open Chat Info |
| `Alt + S` | Settings |
| `Alt + L` | Lock Application |
| `Ctrl + 1..9` | Jump to chat (by position) |

### Message Actions

| Shortcut | Action |
| :--- | :--- |
| `Alt + R` | Reply |
| `Ctrl + Alt + R` | Reply Privately |
| `Ctrl + Alt + D` | Forward |
| `Alt + 8` | Star Message |
| `Ctrl + Up Arrow` | Edit Last Message |
| `Alt + A` | Open Attachment Panel |
| `Ctrl + Alt + E` | Emoji Panel |
| `Ctrl + Alt + G` | GIF Panel |
| `Ctrl + Alt + S` | Sticker Panel |

### Voice Messages (PTT)

| Shortcut | Action |
| :--- | :--- |
| `Shift + .` | Increase Playback Speed |
| `Shift + ,` | Decrease Playback Speed |
| `Ctrl + Enter` | Send Voice Message |
| `Alt + P` | Pause Recording |
| `Ctrl + Alt + Shift + R` | Star Recording |

---

## Enhanced Add-on Features

These tools supplement the native WhatsApp experience, addressing remaining accessibility gaps.

### 1. Advanced Message Reading
If a message is too long or focus becomes unreliable, use these tools for better control.

*   **Context Menu Access (`Shift + Enter`):** Opens the options menu for the focused message. This is designed to work seamlessly across many different languages.
*   **Voice Message Playback (`Enter`):** Allows you to play or pause voice messages instantly by simply pressing Enter while the message is focused.
*   **Text Window View (`Alt + C`):** Opens the focused message in a dedicated, read-only text window. This allows you to navigate line-by-line using standard arrow keys or select specific portions of text. Press `Escape` to close.
*   **Quick Copy (`Ctrl + C`):** Directly copies the text of the focused message bubble to your clipboard.

### 2. Last Spoken Text Review
By default, this add-on **locks Browse Mode to 'Off'** to prevent navigation conflicts. However, this means NVDA's standard review cursor (which relies on the virtual buffer) may not work for reviewing fleeting announcements.

To solve this, we provide a custom review tool that captures the most recent speech output:

| Shortcut | Action |
| :--- | :--- |
| `NVDA + Left/Right Arrow` | Review last spoken text **character by character**. |
| `NVDA + Ctrl + Left/Right Arrow` | Review last spoken text **word by word**. |

### 3. Phone Number Filtering
Group chats often become cluttered with unsaved phone numbers, making chat headers verbose and difficult to follow.

This add-on features an intelligent **filter** that strips phone numbers from object names in both **Speech and Braille**, resulting in a much cleaner interface.

In the message list, only the sender's number is removed. Numbers that people type in a message are kept.

*   **Configuration:** Configure chat-list and message-list filtering separately in the add-on settings. Both commands can also be assigned from NVDA's Input Gestures dialog.

### 4. Smart "Usage Hint" Silencing
WhatsApp often appends repetitive instructions to every chat item (e.g., *"For more options, press left or right arrow..."*). Hearing this on every single chat is tedious and slows down your workflow.

Our filter can identify and **silence these hints**, leaving only the essential information: Chat Name, Message Preview, Time, and Status.

*   **How it works:** The filter removes a hint only from the end of the text, and only when it mentions the keyboard action, while preserving the message and status updates like *"Read"*, *"Delivered"*, *"unread"*, or *"reactions"*.
*   **Configuration:** Hints are read by default. To silence them, turn off the "Read usage hints while navigating chat list" option in the settings panel.

### 5. Virtual Navigation for Inaccessible Menus
Certain parts of the modern WhatsApp interface—such as Settings panels and dialog menus—are difficult to navigate when Browse Mode is disabled. We have transformed these areas into fast, responsive **virtual menus**.

*   **How it works:** When you focus on these dialog areas, NVDA captures the available options into a temporary list.
*   **Virtual Browsing:** Use **Up or Down Arrows** to cycle through the options. NVDA will announce each item (like "Profile", "Chats", "Notifications", or "Status") along with its current state (e.g., "on" or "off"), without shifting your actual focus on the screen.
*   **Quick Activation:** Press **Control + Enter** to immediately trigger the option you have selected.

> [!IMPORTANT]
> This feature is currently **experimental**. While it significantly improves access to previously unreachable menus, we are constantly refining the detection logic. If you have a more efficient method or find a bug, we highly encourage you to contribute via our GitHub repository.

## Feedback & Contributions

We welcome suggestions, bug reports, and code contributions.

*   **Email:** [bredgreene5@gmail.com](mailto:bredgreene5@gmail.com)
*   **GitHub:** Open an issue or submit a Pull Request on the project repository.
