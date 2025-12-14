# FindMyMeal - Automated Restaurant Discovery Platform

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Selenium](https://img.shields.io/badge/Selenium-4.0-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100-teal) ![Docker](https://img.shields.io/badge/Docker-Ready-blue)

A full-stack web application that aggregates restaurant data using web scraping and allows users to search and favorite locations. This project demonstrates a complete **End-to-End (E2E) QA Automation Architecture**.

##  Demo
[link]

## 🏗 Architecture
* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL (SQLModel)
* **Frontend:** Jinja2 Templates + Bootstrap
* **External Integration:** Apify (Google Maps Scraper)
* **Infrastructure:** Docker & Docker Compose

##  Test Automation Strategy
* Uses **Selenium WebDriver** and **Pytest Fixtures**.
* **Pattern:** Implements the *Page Object Model* (POM) concepts and *Atomic Testing*.
* **Features Covered:**
    * Dynamic Data Seeding (SQL Injection for test setup).
    * Race Condition handling with `WebDriverWait`.
    * Chrome Options for bypassing "Breach" and "Safe Browsing" popups.

## How to Run

### Prerequisites
* Docker & Docker Compose
* Python 3.12+

### Quick Start (Docker)
```bash
# 1. Clone the repo
git clone [https://github.com/](https://github.com/)[noorshehab]/FindMyMeal.git

# 2. Build and Run
docker-compose up --build