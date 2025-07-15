# Config Matrix

A comprehensive web application for managing computer setup configurations and tracking technician assignments. Config Matrix streamlines the process of deploying and managing multiple computer configurations across different user profiles with multi-technician support.

## ⚠️ Disclaimer
This software is provided "as is" without warranty of any kind. Use at your own risk.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Application Workflow](#application-workflow)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [License](#license)
- [Deployment](#deployment)
- [Future Enhancements](#future-enhancements)

## 🎯 Overview

Config Matrix is designed for IT departments and system administrators who need to manage multiple computer setups efficiently. The application provides a centralized platform to:

- Create and manage configuration profiles for different use cases (Developer, Creative Professional, Business User, etc.)
- Track setup progress across multiple computers
- Assign multiple technicians to computer configurations
- Monitor completion status and deadlines
- Manage setup steps with download links and documentation

## ✨ Features

### Core Functionality
- **Multi-Technician Support**: Assign multiple technicians to each computer with many-to-many relationships
- **Profile Management**: Create custom setup profiles with specific software and configuration steps
- **Progress Tracking**: Real-time tracking of setup completion across all computers
- **Step Management**: Create, edit, and organize setup steps with download links
- **Deadline Management**: Set and track setup deadlines for each computer
- **Notes System**: Add custom notes to computers for special instructions or tracking

### User Interface
- **Modern Dark Theme**: Professional dark UI with responsive design
- **Interactive Dashboard**: Overview of all computers, profiles, and system status
- **Real-time Filtering**: Filter computers by technician, completion status, and search terms
- **Drag-and-Drop Interface**: Easy profile editing with step management
- **Modal-based Workflows**: Streamlined user experience for complex operations

### Security & Authentication
- **Secure Authentication**: BCrypt password hashing with salt
- **Session Management**: Secure session handling with CSRF protection
- **Input Validation**: Comprehensive form validation and sanitization
- **Password Requirements**: Enforced password complexity rules

### Database Management
- **Robust Database Design**: SQLAlchemy ORM with proper relationships
- **Session Management**: Context managers for proper database session handling
- **Data Integrity**: Foreign key constraints and relationship validation
- **Sample Data Generator**: Built-in script to populate the database with realistic test data

## 🛠 Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask 2.3.3**: Web framework
- **SQLAlchemy 2.0.21**: ORM and database toolkit
- **Flask-Login 0.6.3**: User session management
- **Flask-WTF 1.1.1**: Form handling and CSRF protection
- **BCrypt 4.0.1**: Password hashing and security

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Bootstrap 5.1.3**: UI framework and responsive design
- **Bootstrap Icons**: Comprehensive icon library
- **Vanilla JavaScript**: Dynamic frontend interactions
- **Modern CSS Variables**: Theming and design system

### Database
- **SQLite**: Lightweight database for development and small deployments
- **Configurable**: Easy to switch to PostgreSQL, MySQL, or other databases

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/mitzCanCode/Config-matrix.git
   cd Config-matrix
   ```

2. **Create a Virtual Environment**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   ```bash
   python create_sample_db.py
   ```
   This will create a SQLite database with sample data including:
   - 6 sample technicians (including a 'user' account)
   - 35+ setup steps with real download links
   - 5 pre-configured profiles (Developer, Creative Professional, Business User, etc.)
   - 50+ sample computers with varied progress levels
   - Realistic test data for development and testing

5. **Run the Application**
   ```bash
   python app.py
   ```
   The application will be available at: `http://localhost:9999`

6. **Access the Application**
   - Open your web browser and navigate to `http://localhost:9999`
   - Use the sample credentials:
     - Username: `user`
     - Password: `Password123@`
   - Or register a new account

## 💻 Usage

### Getting Started

1. **Login/Register**: Access the application through the authentication system
2. **Dashboard**: Get an overview of the system status and navigate to different sections
3. **Computers**: View and manage all computers in the system
4. **Profiles**: Create and manage configuration profiles
5. **Setup Process**: Track individual computer setup progress

### Sample Accounts

The sample database includes several pre-configured technician accounts:

| Username | Password | Role |
|----------|----------|------|
| user | Password123@ | Standard User |
| Alice Johnson | SecurePass2024! | Technician |
| Robert Chen | TechSupport#789 | Technician |
| Maria Rodriguez | ITAdmin$456 | Technician |
| James Wilson | ConfigMaster@123 | Technician |
| Sarah Kim | SystemSetup@321 | Technician |

## 📱 Application Workflow

### 1. Profile Creation
```
Dashboard → Profiles → Add Profile → Configure Steps → Save
```
- Create profiles for different use cases (Developer, Creative, Business)
- Add relevant setup steps with download links
- Organize steps in logical order

### 2. Computer Management
```
Dashboard → Computers → Add Computer → Assign Profile & Technicians → Track Progress
```
- Add new computers to the system
- Assign appropriate profiles and technicians
- Set deadlines and add notes
- Monitor setup progress

### 3. Setup Process
```
Computers → Select Computer → Setup Interface → Toggle Steps → Complete Setup
```
- Access individual computer setup pages
- Mark steps as complete/incomplete
- Edit computer details (name, deadline, technicians, notes)
- Track overall progress

### 4. Multi-Technician Assignment
```
Computer → Edit → Select Multiple Technicians → Save
```
- Assign multiple technicians to a single computer
- Track who is working on what
- Collaborative setup management

## 🗄 Database Schema

### Core Tables

**Technicians**
- `id` (Primary Key)
- `name` (String, Required)
- `password` (String, Hashed)

**Profiles**
- `id` (Primary Key)
- `name` (String, Required)

**SetupSteps**
- `id` (Primary Key)
- `name` (String, Required)
- `download_link` (String, Optional)

**Computers**
- `id` (Primary Key)
- `name` (String, Required)
- `deadline` (DateTime, Optional)
- `profile_id` (Foreign Key)
- `notes` (String, Optional)

### Association Tables

**computer_technician_association**
- Many-to-many relationship between Computers and Technicians

**profile_step_association**
- Many-to-many relationship between Profiles and SetupSteps

**computer_step_association**
- Many-to-many relationship between Computers and SetupSteps (completed steps)

## 🔗 API Endpoints

### Authentication
- `GET /` - Landing page
- `GET /login` - Login page
- `POST /login` - Authentication
- `GET /register` - Registration page
- `POST /register` - User registration
- `GET /logout` - User logout

### Computers
- `GET /api/computers` - List all computers
- `POST /api/add_computer` - Create new computer
- `GET /api/computer_info/<name>` - Get computer details
- `GET /api/computer_setup/<name>` - Get setup information
- `POST /api/edit_computer` - Edit computer details
- `POST /api/delete_computer` - Delete computer
- `POST /api/toggle_step` - Toggle step completion

### Profiles
- `GET /api/profiles` - List all profiles
- `POST /api/add_profile` - Create new profile
- `GET /api/profile/<id>` - Get profile details
- `POST /api/profile/<id>/steps` - Add step to profile
- `DELETE /api/profile/<id>/steps/<step_id>` - Remove step from profile
- `DELETE /api/profile/<id>/delete` - Delete profile

### Steps
- `POST /api/steps` - Create new step
- `PUT /api/steps/<id>` - Edit step
- `POST /api/steps/create-and-add` - Create step and add to profile
- `POST /api/steps/<id>/delete` - Delete step

### Technicians
- `GET /api/technicians` - List all technicians

## 📸 Screenshots

### Dashboard
The main dashboard provides an overview of the system with navigation to computers and profiles.

### Computer Management
- **List View**: Grid of computer cards showing progress, deadlines, and assignments
- **Filters**: Search by name, filter by technician, completion status toggles
- **Multi-select**: Assign multiple technicians to computers

### Profile Management
- **Profile List**: Overview of all configuration profiles
- **Profile Editor**: Drag-and-drop interface for managing setup steps
- **Step Management**: Create, edit, and organize setup steps

### Setup Interface
- **Progress Tracking**: Visual representation of completed/remaining steps
- **Step Details**: Download links and instructions for each step
- **Computer Info**: Edit computer details directly from setup page

### Development Setup

1. Follow the installation instructions above
2. Run the application in debug mode:
   ```bash
   python app.py
   ```
3. The application will reload automatically when you make changes



## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set up proper environment variables for production
2. **Database**: Switch to PostgreSQL or MySQL for production use
3. **Security**: Enable HTTPS and secure session cookies
4. **Authentication**: Consider implementing OAuth or LDAP integration
5. **Logging**: Set up proper logging and monitoring
6. **Backup**: Implement regular database backups

### Docker Deployment (Future)

A Dockerfile and docker-compose configuration will be added in future releases for easy deployment.

## 🔮 Future Enhancements

- **Email Notifications**: Automated deadline reminders

---


**Config Matrix** - Streamlining computer setup management for IT professionals.
