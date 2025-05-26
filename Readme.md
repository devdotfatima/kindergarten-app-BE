# Kindergarten Communication API v1

RESTful API for managing a Kindergarten Communication System

---

## Base URL

http://16.171.16.72:8000/

## API Documentation

Explore the interactive API documentation (Swagger UI):  
[http://16.171.16.72:8000/swagger/](http://16.171.16.72:8000/swagger/)

---

## Overview

This API provides endpoints to manage all aspects of a kindergarten communication platform, including:

- Activities  
- Attendance  
- Children management  
- Classes and Teachers  
- Comments and Likes  
- Dashboard statistics  
- Hygiene tracking  
- Kindergarten info and admin management  
- Meals and Moods  
- Naps  
- Notifications  
- Posts  
- Teacher Classes  
- User authentication and registration

---

## Authentication

- Login via username/password or PIN  
- User registration (Admin, Parent, Teacher)  
- Profile editing and password update  
- Logout endpoint  
- Token-based authorization (using Django Login / JWT or session)

---

## Key Endpoints Summary

### Activities
- `GET /activities/` - List activities  
- `POST /activities/` - Create activity  
- `GET /activities/{id}/` - Retrieve activity details  
- `PUT/PATCH /activities/{id}/` - Update activity  
- `DELETE /activities/{id}/` - Delete activity  

### Attendance
- `GET /attendance/` - List attendance records  
- `POST /attendance/` - Create attendance  
- `GET /attendance/by-child/{child_id}/` - Attendance for a specific child  
- `GET /attendance/by-child/{child_id}/by-date/` - Attendance for a child filtered by date  

### Children
- CRUD endpoints to manage children  

### Classes
- `GET /classes/teachers` - List all teachers by class  
- `GET /classes/{class_id}/children/` - List children in a class  

### Comments
- Full CRUD + toggle like for comments on posts or activities  

### Dashboard
- Cards and charts statistics for overview metrics  

### Hygiene, Meals, Moods, Naps
- Full CRUD for daily tracking of hygiene, meals, moods, and naps  

### Kindergarten
- Manage kindergartens, classes, and attach/detach admins  

### Notifications
- List, send, mark read, and delete notifications  

### Posts
- Create, read, update, delete posts  
- Filter posts by class or kindergarten  
- Toggle like on posts  

### Teachers and Teacher Classes
- Manage teacher profiles and their class assignments  

### Users and Authentication
- Login, logout, register users  
- Profile and password management  
- Set PIN for login with PIN  

---

## Contact

For support or inquiries, please contact the developer.

---

## Usage Example

```bash
# List all children
curl http://16.171.16.72:8000/children/

# Create a new activity
curl -X POST http://16.171.16.72:8000/activities/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Painting Class", "description": "Art session for kids"}'

# Login
curl -X POST http://16.171.16.72:8000/users/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "parent1", "password": "securepassword"}'


Notes
	•	Ensure you have proper authorization headers for endpoints requiring authentication.
	•	Refer to the Swagger documentation for full request/response schemas and filters.