# 🚨 AI-Based Offline Disaster Reporting and Intelligent Emergency Coordination System

An AI-assisted disaster reporting and emergency coordination platform built with **Python, Flask, Machine Learning, SQLite, HTML, CSS, and JavaScript**.

The system allows citizens to submit emergency reports with GPS location, descriptions, and optional evidence photos. The application analyzes each report, estimates severity, calculates priority, detects similar reports, and provides authorities with a centralized response dashboard for managing emergencies and rescue-team assignments.

---

## 📌 Project Overview

During disasters such as floods, earthquakes, fires, and cyclones, emergency reports can be incomplete, duplicated, or difficult to prioritize manually.

This project provides a local software-based workflow that connects:

**Citizen Reporting → AI/ML Analysis → Priority Calculation → Authority Dashboard → Rescue Team Assignment → Status Tracking**

The system is designed around local processing and does not require an external AI API for its core prototype workflow.

---

## 🎯 Problem Statement

During disasters, affected people may need to communicate emergencies such as flooding, injuries, trapped persons, structural damage, fires, and other dangerous situations.

Emergency response can become difficult when:

- reports are unstructured
- multiple people report the same incident
- emergencies have different severity levels
- response teams need to prioritize incidents
- location information needs to be captured quickly
- authorities need to track response progress

The project addresses these challenges by transforming citizen emergency reports into structured information for emergency coordination.

---

## 💡 Proposed Solution

The system allows citizens to submit:

- emergency description
- GPS location
- optional evidence image

The application then performs automated processing:

1. Disaster type classification
2. Severity prediction
3. Similar/duplicate report detection
4. Priority calculation
5. Report storage
6. Authority response management
7. Rescue-team assignment
8. Status history tracking

---

## ✨ Key Features

### 👤 Citizen Features

- 🚨 Emergency report submission
- 📍 Browser-based GPS detection
- 📝 Emergency description
- 📸 Evidence image upload
- 🤖 Automated disaster classification
- ⚠️ Severity estimation
- 🔍 Similar/related report detection
- 📊 Priority score calculation
- 📋 View submitted reports
- 🔎 Track reports using Report ID
- 🕒 View response history
- 🗺️ Open emergency coordinates in Google Maps

### 🔐 Authority Features

- Authority login
- 📊 Emergency response dashboard
- 📈 Report statistics and analytics
- 🗺️ Emergency map
- 🔎 Search and filtering
- 🚨 Priority-based response queue
- 📋 Detailed emergency reports
- 📸 Evidence review
- 📍 GPS/location review
- 📌 Status management
- 🕒 Response history
- 🚑 Rescue-team management
- 👥 Rescue-team assignment
- 🔓 Release rescue-team assignments
- 💾 Persistent team assignments

---

## 🧠 AI / Machine Learning Components

### 1. Disaster Classification

The project uses **TF-IDF text representation with Logistic Regression** for disaster-type classification.

Currently supported disaster categories include:

- Flood
- Earthquake
- Fire
- Cyclone

---

### 2. Severity Prediction

The current implementation uses a lightweight rule-based text analysis approach.

Emergency descriptions are analyzed for severity-related keywords such as:

- death
- dead
- trapped
- injured
- collapsed
- destroyed
- severe
- critical
- urgent

The system produces:

- Low
- Medium
- High

---

### 3. Similarity / Duplicate Detection

The system uses:

- TF-IDF vectorization
- cosine similarity

to compare a newly submitted report with previously stored reports.

Similarity is categorized as:

- Duplicate
- Related
- No Match

This helps reduce repeated reports and identify incidents that may describe the same emergency.

---

### 4. Priority Calculation

Priority is calculated from:

- severity
- disaster type

The system generates:

- priority category
- priority score out of 100

Priority categories include:

- Critical
- High
- Medium
- Low

---

## 🔄 System Workflow

```text
                ┌──────────────────────┐
                │      Citizen         │
                │  Submits Emergency   │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   GPS + Description  │
                │   + Evidence Image   │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Disaster Type      │
                │   Classification     │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Severity Prediction  │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Similarity /         │
                │ Duplicate Detection  │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Priority Calculation │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │    SQLite Storage    │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Authority Dashboard  │
                └──────────┬───────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
   ┌────────────────────┐      ┌────────────────────┐
   │ Assign Rescue Team │      │ Update Status      │
   └──────────┬─────────┘      └──────────┬─────────┘
              │                           │
              └─────────────┬─────────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Response History /   │
                 │ Emergency Tracking   │
                 └──────────────────────┘
🛠️ Technologies Used
Backend
Python
Flask
Flask-SQLAlchemy
SQLite
Frontend
HTML5
CSS3
JavaScript
Machine Learning / NLP
Scikit-learn
NumPy
Pandas
TF-IDF
Logistic Regression
Cosine Similarity
Rule-based severity analysis
Weighted priority logic
Mapping
Browser Geolocation API
Google Maps links
Leaflet-based map functionality in the authority interface
📂 Project Structure
disaster-response/
│
├── app.py
│
├── backend/
│   ├── rescue_team.py
│   └── response_queue.py
│
├── ml/
│   ├── disaster_classifier.py
│   ├── priority.py
│   ├── severity_predictor.py
│   └── similarity.py
│
├── templates/
│   ├── index.html
│   ├── report.html
│   ├── report_success.html
│   ├── reports.html
│   ├── track_report.html
│   ├── track_report_result.html
│   │
│   └── authority/
│       ├── dashboard.html
│       ├── login.html
│       └── report_details.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── location_legacy.js
│   │
│   └── uploads/
│
├── instance/
│   └── disaster.db
│
├── requirements.txt
├── .gitignore
└── README.md
