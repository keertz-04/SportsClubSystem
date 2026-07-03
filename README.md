# 🏆 Sports Club Management System

A web-based application that helps manage sports club activities efficiently. It allows administrators to manage events and members, while users can register, view events, and track their participation through a simple and secure interface.

## 🚀 Features

### Admin
- Secure Login (JWT Authentication)
- Manage Sports Events
- Manage Members
- View Event Registrations
- Approve or Reject Registrations
- Post Announcements
- Dashboard with Statistics

### User
- Register and Login
- View Sports Events
- Register for Events
- View Registration Status
- Update Profile
- View Announcements

## 🛠️ Technologies Used

**Frontend**
- React.js
- HTML
- CSS
- Bootstrap / Tailwind CSS

**Backend**
- Node.js
- Express.js

**Database**
- MongoDB
- Mongoose

**Authentication**
- JWT
- bcrypt.js

## 📂 Project Structure

```
sports-club-system/
│── client/
│── server/
│── README.md
│── package.json
```

## ⚙️ Installation

1. Clone the repository

```bash
git clone https://github.com/your-username/sports-club-system.git
```

2. Install dependencies

```bash
cd server
npm install

cd ../client
npm install
```

3. Create a `.env` file inside the **server** folder.

```env
PORT=5000
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_secret_key
```

4. Run the application

Backend

```bash
cd server
npm start
```

Frontend

```bash
cd client
npm start
```

## 🔐 Authentication

The application uses **JWT (JSON Web Token)** for secure authentication and **bcrypt** for password encryption.

## 🌟 Future Enhancements

- Online Payment Integration
- Email Notifications
- QR Code Event Check-in
- Attendance Tracking
- Mobile Application

## 👩‍💻 Author

**Keerthiga**

Bachelor of Information Technology

## 📄 License

This project is developed for educational and academic purposes.
