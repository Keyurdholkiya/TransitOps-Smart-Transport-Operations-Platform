<div align="center">

# 🚛 TransitOps
### Smart Transport Operations Platform

🚀 A modern fleet and transport management platform built for the **Odoo Hackathon 2026**.

<h1>▦</h1>

![HTML](https://img.shields.io/badge/Frontend-HTML5-orange?style=for-the-badge&logo=html5)
![CSS](https://img.shields.io/badge/CSS3-Blue?style=for-the-badge&logo=css3)
![JavaScript](https://img.shields.io/badge/JavaScript-yellow?style=for-the-badge&logo=javascript)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)

---

### 🎯 "Digitizing Fleet Operations with Smart Automation"

</div>

---

# 📖 Overview

TransitOps is a centralized transport management platform designed to simplify fleet operations, driver management, trip planning, maintenance tracking, and operational analytics.

The platform replaces manual spreadsheets and paper-based workflows with a secure, modern, and intelligent web application.

---

# ✨ Key Features

## 🔐 Authentication
- Secure Login
- Role-Based Access Control (RBAC)
- JWT Authentication

## 📊 Dashboard
- Active Vehicles
- Available Vehicles
- Vehicles in Maintenance
- Active Trips
- Fleet Utilization
- Operational KPIs

## 🚛 Vehicle Registry
- Register Vehicles
- Vehicle Status Tracking
- Capacity Management
- Odometer Tracking

## 👨‍✈️ Driver Management
- Driver Profiles
- License Validation
- Safety Score
- Driver Availability

## 🚚 Trip Management
- Create Trips
- Vehicle Assignment
- Driver Assignment
- Cargo Validation
- Automatic Status Updates

## 🔧 Maintenance
- Maintenance Logs
- Vehicle Availability
- Service History

## ⛽ Fuel & Expenses
- Fuel Logs
- Toll Expenses
- Maintenance Cost
- Operational Cost Tracking

## 📈 Analytics
- Fuel Efficiency
- Fleet Utilization
- Vehicle ROI
- Cost Analysis

---

# 🏗 Project Architecture

```
Frontend (HTML + CSS + JavaScript)
            │
            ▼
      FastAPI Backend
            │
            ▼
      PostgreSQL Database
```

---

# 🗂 Project Structure

```
TransitOps
│
├── frontend
│   ├── index.html
│   ├── dashboard.html
│   ├── vehicles.html
│   ├── drivers.html
│   ├── trips.html
│   ├── css/
│   ├── js/
│   └── assets/
│
├── backend
│
├── docker-compose.yml
│
└── README.md
```

---

# 🛠 Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI |
| Database | PostgreSQL |
| Authentication | JWT |
| API Documentation | Swagger |
| Deployment | Docker |

---

# 👥 User Roles

- 🚛 Fleet Manager
- 🚚 Dispatcher
- 🛡 Safety Officer
- 💰 Financial Analyst

---

# 🔄 Workflow

```
Login
   │
   ▼
Dashboard
   │
   ├── Vehicle Registry
   ├── Driver Management
   ├── Trip Management
   ├── Maintenance
   ├── Fuel Logs
   └── Reports & Analytics
```

---

# 📸 Screens

- 🔐 Login
- 📊 Dashboard
- 🚛 Vehicle Registry
- 👨 Driver Management
- 🚚 Trip Dispatcher

---

# 🎯 Business Rules

- Vehicle Registration Number must be unique.
- Expired License Drivers cannot be assigned.
- Suspended Drivers cannot be assigned.
- Cargo Weight must not exceed Vehicle Capacity.
- Vehicles under Maintenance cannot be dispatched.
- Driver and Vehicle status update automatically during Trip lifecycle.

---

# 🚀 Future Enhancements

- Email Notifications
- GPS Tracking
- QR Code Vehicle Management
- Predictive Maintenance
- AI-based Route Optimization
- Mobile Application

---

# 👨‍💻 Team

| Member | Responsibility |
|----------|---------------|
| Keyur | Frontend Development |
| Harvin | Backend Development |
| Vidhi | Integration & Testing |
| nagma | Frontend Development |

---

# ❤️ Built for

## Odoo Hackathon 2026

Developed with passion to modernize transport operations through automation, real-time insights, and secure fleet management.

---

<div align="center">

### ⭐ Thank You ⭐

**If you like this project, don't forget to give it a ⭐ on GitHub!**

Made with ❤️ by Team TransitOps

</div>
