# Car Voice Assistant - Setup Guide

A voice-controlled driving assistant that lets you play music, take notes, and interact hands-free while on the road. Designed for safety, simplicity, and seamless in-car use, powered by natural speech and lightweight on-device logic.

## Prerequisites
- Android Phone
- [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm) (Paid app, ~$3.50)
- [Termux](https://f-droid.org/en/packages/com.termux/) (Free, get it from F-Droid, NOT Play Store, so first download F-Droid)
- Spotify Account (Premium for POST requests on Spotify API, like playing a playlist)

---

## Part 1: The Brain (Termux Setup)

1.  **Install Python**
    Open Termux and run:
    ```bash
    pkg update && pkg upgrade
    pkg install python
    ```

2.  **Transfer Files**
    You need to get `cerebro.py` and `requirements.txt` into your phone, here I opt for the Download folder.
    In Termux:
        ```bash
        termux-setup-storage
        cp /storage/emulated/0/Download/cerebro.py ~/
        cp /storage/emulated/0/Download/requirements.txt ~/
        ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    Warning: it's possible that you need some ubuntu distro and a venv to make all the dependencies work.

4.  **Configure Environment**
    You need to set your Spotify credentials. Tutorial [here](https://developer.spotify.com/documentation/web-api/tutorials/getting-started). Set the credentials in the cerebro.py file.


5.  **Run the Server**
    ```bash
    python cerebro.py
    ```
    You should see: `Uvicorn running on http://0.0.0.0:9000`

---

## Part 2: The Ear (Tasker Setup)

### 1. Install Hotword Plugin
- Install "Hotword Plugin Free" from Play Store.
- Follow the instructions in the app to create as many models as wake words you want.
- Save those models (`.pmdl`) on your phone.
- Import the models the Hotword Plugin app.

### 2. Configure "Música Maestro" Profile
1.  **New Profile** -> Event -> Plugin -> Hotword Plugin.
2.  Click on the pencil in configuration and select your `MusicaMaestro` model.
3.  Go back.
4.  **New Task** -> "Play Music":
    *   Action: Net --> **HTTP Post**
    *   Server:port --> localhost:9000/
    *   URL --> music

### 3. Configure "Apunta esto" Profile
1.  **New Profile** -> Event -> Plugin -> Hotword Plugin.
2.  Click on the pencil in configuration and select your `ApuntaEsto` model.
3.  Go back.
4.  **New Task** -> "Take Note":
    *   Action 1: **Get Voice** (Language: Spanish). This will listen and save to `%VOICE`.
    *   Action 2: **HTTP Request**
        *   Method: `POST`
        *   URL: `http://localhost:9000/note`
        *   Body: `{"text": "%VOICE"}`
        *   Headers: `Content-Type: application/json`
    *   Action 3 (Optional): **Say** -> Text: "Anotado".

---

## Part 3: Testing
1.  Ensure `cerebro.py` is running in Termux and Hotword Plugin is listening.
2.  Say "Música Maestro". Spotify should start shuffling your playlist.
3.  Say "Apunta esto", wait for the beep, say "Comprar pan", and check `notas_coche.md` in Termux (or check the server logs).