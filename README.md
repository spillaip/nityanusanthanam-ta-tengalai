# 📿 நித்யானுசந்தானம் (Nithyanusandhanam)

An elegant, mobile-responsive web application built with **Streamlit** to facilitate the daily recitation (*Anusandhanam*) of sacred Tamil hymns from the **Nalayira Divya Prabandham**.

[Nithyanusandhanam](https://www.NirmalamGroup.in) 

---

## ✨ Key Features

* **📖 Comprehensive Collection:** Access various sections including *Thiruppallandu*, *Thiruppavai*, *Amalanadipiran*, and more via an intuitive sidebar.
* **🔊 Audio Integration:** Integrated **Google Text-to-Speech (gTTS)** support allows users to listen to the hymns in native Tamil.
* **🔍 Smart Search:** Real-time filtering of *Taniyans* and *Pasurams* to find specific verses instantly.
* **🔗 Deep Linking:** Share specific verses with friends or family via URL parameters (e.g., `?section=Thiruppavai&pasuram=1`).
* **🎨 Premium UI/UX:**
    * Custom CSS for an "App-like" mobile experience.
    * Automatic **Light and Dark mode** support.
    * High-readability typography specifically tuned for Tamil script.

---

## 🛠️ Technical Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python-based web framework).
* **TTS Engine:** `gTTS` (Google Text-to-Speech) for Tamil vocalization.
* **Data Structure:** Python `dataclasses` for structured hymn parsing.
* **Styling:** Custom CSS injection for linear gradients, glassmorphism effects, and responsive layout containers.

---

## 📁 Project Structure

```text
├── app.py              # Main Streamlit application
├── assets/             # Images and branding icons
├── pasurams/           # Source text files (.txt) for each section
└── requirements.txt    # Project dependencies
```

## 🚀 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/nithyanusandhanam.git
    cd nithyanusandhanam
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

---

## 📝 Data Format
The application uses a custom tag-based parsing system to render content beautifully. Source files in the `/pasurams` folder follow this structure:

```text
<title>Section Title</title>
[taniyan]
<heading>Author Name</heading>
Verse lines go here...
---
[pasuram]
Verse lines go here...
```

---

## ❤️ Contribution & Effort
This project is an effort to keep our tradition accessible in the digital age. 

Developed with devotion by [Nirmalam Group](https://www.NirmalamGroup.in). 

---
*If you find this project helpful, please consider giving it a ⭐ on GitHub!*
