# 🏛️ SmartGriev — AI-Powered Public Grievance Management System

> A full-stack Django web application enabling citizens to submit municipal complaints, with AI-driven classification, priority scoring, duplicate detection, and an admin command center.

---

## 🚀 Features at a Glance

| Feature | Description |
|---|---|
| 🤖 **AI Classification** | TF-IDF + Logistic Regression auto-categorizes complaints |
| 📊 **Priority Scoring** | Rule-based + sentiment scoring (0–100 scale) |
| 🔍 **Duplicate Detection** | Cosine similarity identifies similar complaints |
| ⏱️ **SLA Prediction** | Estimates resolution time based on category & priority |
| 💬 **Sentiment Analysis** | Analyzes complaint urgency from text tone |
| 🗺️ **Location Mapping** | Interactive Leaflet.js maps for location tracking |
| 📈 **Admin Dashboard** | Real-time charts, stats, and complaint management |
| 🔐 **Role-Based Auth** | Citizen & Admin roles with restricted access |
| 📱 **Responsive UI** | Bootstrap 5 with government-style professional theme |

---

## 📁 Project Structure

```
grievance_system/
├── config/                    # Django project configuration
│   ├── settings.py            # Settings (SQLite, static, media)
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py                # WSGI application
│
├── grievance_portal/          # Main Django app
│   ├── models.py              # User, Complaint, DuplicateMapping, Timeline
│   ├── views.py               # All views (citizen + admin)
│   ├── forms.py               # Registration, Login, Complaint forms
│   ├── urls.py                # App URL patterns
│   ├── admin.py               # Django admin configuration
│   ├── apps.py                # App config (AI engine pre-load)
│   ├── templatetags/          # Custom template filters
│   │   └── custom_tags.py
│   ├── management/commands/   # Management commands
│   │   └── seed_data.py       # Demo data seeder
│   └── templates/
│       ├── grievance_portal/  # Citizen-facing templates
│       │   ├── base.html
│       │   ├── home.html
│       │   ├── submit_complaint.html
│       │   ├── my_complaints.html
│       │   ├── complaint_detail.html
│       │   └── notifications.html
│       ├── registration/      # Auth templates
│       │   ├── login.html
│       │   └── register.html
│       └── admin_panel/       # Admin templates
│           ├── dashboard.html
│           ├── complaints.html
│           ├── duplicates.html
│           └── analytics.html
│
├── ai_engine/                 # Pure-Python AI Engine (no sklearn dependency)
│   └── __init__.py            # TF-IDF, Logistic Regression, Sentiment, Cosine Similarity
│
├── media/                     # Uploaded complaint images
├── models_pkl/                # (Optional) Saved model cache
├── manage.py
├── requirements.txt
├── setup.sh                   # Quick setup script
└── README.md
```

---

## 🛠️ Quick Setup

### Prerequisites
- Python 3.10+
- pip

### Option 1: Auto Setup Script
```bash
git clone <repo>
cd grievance_system
chmod +x setup.sh
./setup.sh
python manage.py runserver
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 3. Create superuser (or use seed_data)
python manage.py createsuperuser

# 4. Seed demo data (optional but recommended)
python manage.py seed_data

# 5. Run server
python manage.py runserver
```

### Access the Application
| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Home page |
| `http://127.0.0.1:8000/login/` | Login |
| `http://127.0.0.1:8000/register/` | Register |
| `http://127.0.0.1:8000/submit-complaint/` | Submit complaint |
| `http://127.0.0.1:8000/my-complaints/` | Track complaints |
| `http://127.0.0.1:8000/dashboard/` | Admin dashboard |
| `http://127.0.0.1:8000/admin/` | Django admin |

---

## 🔑 Demo Credentials (after seed_data)

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Citizen | `citizen` | `citizen123` |
| Citizen | `priya` | `priya123` |

---

## 🤖 AI Engine Architecture

The AI engine (`ai_engine/__init__.py`) is a **pure-Python implementation** with no heavy external ML library required at runtime:

### 1. Text Classification
- **Algorithm**: TF-IDF vectorization + Logistic Regression (from-scratch implementation)
- **Categories**: Road, Water, Drainage, Electricity, Garbage, Parks, Noise, Building, Traffic, Other
- **Training**: 60+ curated complaint samples with gradient descent optimization

### 2. Sentiment Analysis
- **Algorithm**: Lexicon-based with intensifier weighting
- **Output**: Score (-1 to +1) + Label (positive/neutral/negative)

### 3. Priority Scoring
- **Algorithm**: Base category priority + keyword boost + sentiment adjustment
- **Output**: Score (0–100) + Level (low/medium/high/critical)

### 4. Duplicate Detection
- **Algorithm**: TF-IDF vectorization + Cosine Similarity
- **Threshold**: 75% similarity triggers duplicate flag

### 5. SLA Prediction
- **Algorithm**: Rule-based lookup table (category × priority_level → days)
- **Output**: Estimated days + expected resolution date

---

## 🗄️ Database Models

```python
User           → Extended AbstractUser with role field
Complaint      → Core complaint model (AI fields + workflow)
DuplicateMapping → Links duplicate to master complaint
ComplaintTimeline → Status change audit trail
Notification   → Citizen alerts on status updates
```

---

## 🔒 Security Features

- CSRF protection on all forms
- Secure password hashing (Django default)
- Role-based access control (admin/citizen)
- File upload validation (type + size)
- SQL injection prevention (Django ORM)
- Input validation on all forms

---

## 🌐 Deployment (Production)

### Environment Variables (.env)
```env
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### PythonAnywhere
1. Upload project to `/home/<username>/grievance_system`
2. Create virtual environment and install requirements
3. Configure WSGI file: `config.wsgi`
4. Set static files: `/static/` → `/home/<username>/grievance_system/staticfiles`
5. Set media files: `/media/` → `/home/<username>/grievance_system/media`

### Render.com
1. Connect GitHub repository
2. Build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
3. Start command: `gunicorn config.wsgi`
4. Set environment variables in dashboard

---

## 📊 API Endpoint

### POST `/api/predict/`
Real-time AI prediction for complaint text (used by submit form live preview).

**Request:**
```json
{
  "title": "Pothole on road",
  "description": "Large dangerous pothole causing accidents"
}
```

**Response:**
```json
{
  "category": "road",
  "priority_score": 72,
  "priority_level": "high",
  "sentiment_label": "negative",
  "estimated_resolution_days": 7
}
```

---

## 📈 Future Enhancements

- [ ] PostgreSQL migration (settings already structured for it)
- [ ] Email notifications (SMTP integration)
- [ ] Mobile app (REST API via DRF)
- [ ] Department portal login
- [ ] GIS heatmap analytics
- [ ] WhatsApp/SMS status alerts
- [ ] OCR for image-based complaint text extraction
- [ ] Multi-language support

---

## 🧑‍💻 Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 + Python 3.10+ |
| Database | SQLite (prod-ready for PostgreSQL) |
| Frontend | Bootstrap 5, Chart.js, Leaflet.js |
| AI/ML | Pure Python (TF-IDF, Logistic Regression, Cosine Similarity) |
| Auth | Django built-in authentication |
| Maps | OpenStreetMap + Leaflet.js |
| Charts | Chart.js 4 |
| Icons | Bootstrap Icons |

---

*Built as a demonstration of AI-driven civic technology for smart governance.*
