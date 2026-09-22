
# Landsat Fetch Pipeline: Geospatial Automation Agent

An asynchronous, web-based geospatial application that allows users to define a geographic Area of Interest (AOI) and automatically fetch the latest Landsat Collection 2 satellite imagery. 

Built with a focus on non-blocking background processing, this pipeline utilizes the Microsoft Planetary Computer STAC API to dynamically query, authenticate, and download remote sensing data, followed by an automated email notification system.

## 🏗️ System Architecture

* **Frontend:** Vanilla JavaScript, HTML5, CSS3, integrated with **Leaflet.js** and Leaflet Draw for interactive spatial bounding box creation.
* **Backend API:** **Flask** (Python) utilizing the Application Factory pattern for scalable RESTful endpoints.
* **Database:** **SQLite** for robust task tracking and state management (Pending, Running, Completed, Failed).
* **Geospatial Engine:** `pystac-client`, `shapely`, and `planetary-computer` for querying and authenticating Spatiotemporal Asset Catalog (STAC) data.
* **Task Queue:** Python `threading` for non-blocking background downloads.
* **Notification System:** Python `smtplib` for automated email dispatch.

## ✨ Key Features

* **Interactive Map UI:** Users can visually draw extraction polygons directly on a global map.
* **Asynchronous Processing:** The web server remains highly responsive by delegating heavy satellite image downloads to a background worker thread.
* **Real-time Status Polling:** The frontend actively polls the SQLite database to update the user on their specific Task ID progress.
* **Automated STAC Queries:** Translates user GeoJSON into bounding boxes to query the Planetary Computer catalog for Landsat 8/9 imagery.
* **Email Notifications:** Automatically alerts the user upon successful download or failure.

## 🚀 Local Setup & Installation

### 1. Prerequisites
Ensure you have [Conda](https://docs.conda.io/en/latest/) installed on your system.

### 2. Clone the Repository
```bash
git clone [https://github.com/ajaypalsinghtuli/landsat-fetch-pipeline.git](https://github.com/ajaypalsinghtuli/landsat-fetch-pipeline.git)
cd landsat-fetch-pipeline

```

### 3. Create the Environment

Create an isolated environment using Python 3.12:

```bash
conda create -n simople python=3.12.13 -y
conda activate simople
pip install -r requirements.txt

```

### 4. Configure Environment Variables

Create a `.env` file in the root directory to store your email credentials securely. You must use a Google App Password, not your standard account password.

```text
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-character-app-password

```

### 5. Run the Application

Start the Flask development server:

```bash
python run.py

```

Access the application in your browser at `http://127.0.0.1:5010`.

## 💻 Usage

1. Open the web interface.
2. Use the polygon or rectangle tool on the map to draw your Area of Interest (AOI).
3. Input your email address and select a date range.
4. Click **Submit Job**.
5. The system will generate a unique Task ID, process the spatial query in the background, download the satellite imagery to the local `instance/downloads` folder, and send a completion email.

## 🛡️ License

This project is open-source and available for community use.
