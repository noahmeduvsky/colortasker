# ColorTasker

A modern, collaborative task management web application built with Flask that helps teams organize and track their work with color-coded tasks, folder organization, and real-time collaboration features.

## Features

### Task Management
- Create, edit, and delete tasks with custom colors
- Set deadlines and add detailed descriptions
- Mark tasks as complete with visual indicators
- Color-coded task organization for easy visual identification

### Folder Organization
- Organize tasks into custom folders
- Create, rename, and delete folders
- Hierarchical task organization for better project management

### Collaboration
- Invite team members to tasks via email
- Add friends and collaborate on shared tasks
- Real-time task sharing and updates
- Comment system for task discussions

### Calendar Integration
- Monthly calendar view of all tasks
- Visual deadline tracking
- Easy navigation between months
- Today's tasks highlighted

### User Management
- Secure user authentication and registration
- User profiles with friend connections
- Search functionality to find team members
- Privacy controls for personal and shared content

### Modern Interface
- Responsive design for desktop and mobile
- Intuitive dashboard with sidebar navigation
- Clean, modern UI with smooth interactions
- Real-time updates without page refresh

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript
- **Forms**: WTForms with CSRF protection
- **Database Migrations**: Flask-Migrate (Alembic)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/colortasker.git
   cd colortasker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r colortasker/requirements.txt
   ```

5. **Set up the database**
   ```bash
   cd colortasker
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your web browser and navigate to `http://localhost:5000`

## Usage

### Getting Started
1. Register a new account or log in with existing credentials
2. Create your first folder to organize tasks
3. Add tasks to folders with custom colors and deadlines
4. Invite team members to collaborate on tasks

### Creating Tasks
1. Navigate to a folder from the sidebar
2. Click "Create Task" button
3. Fill in task details:
   - Task name (required)
   - Description (optional)
   - Deadline (optional)
   - Color (choose from color picker)
4. Click "Create" to save the task

### Collaborating
1. Open any task you own
2. Use the "Invite User" feature to add team members by email
3. Add comments to discuss task details
4. Share tasks with friends from your friends list

### Calendar View
1. Click the calendar icon in the sidebar
2. Navigate between months using arrow buttons
3. View all tasks with deadlines for each day
4. Click on tasks to view details

## Project Structure

```
colortasker/
├── app.py                          # Main application entry point
├── colortasker/
│   ├── __init__.py                 # Flask app factory
│   ├── config.py                   # Configuration settings
│   ├── extensions.py               # Flask extensions setup
│   ├── controllers/                # Route handlers
│   │   ├── auth.py                 # Authentication routes
│   │   ├── main.py                 # Main application routes
│   │   └── errors.py               # Error handling routes
│   ├── models/                     # Database models
│   │   └── models.py               # User, Task, Folder, Comment models
│   ├── templates/                  # HTML templates
│   │   ├── auth/                   # Authentication templates
│   │   ├── errors/                 # Error page templates
│   │   ├── base.html               # Base template
│   │   ├── dashboard.html          # Main dashboard
│   │   └── calendar.html           # Calendar view
│   ├── static/                     # Static files
│   │   ├── css/                    # Stylesheets
│   │   ├── js/                     # JavaScript files
│   │   └── images/                 # Images and icons
│   ├── tests/                      # Test files
│   ├── migrations/                 # Database migrations
│   └── requirements.txt            # Python dependencies
└── logs/                          # Application logs
```

## Database Models

- **User**: User accounts with authentication
- **Folder**: Task organization containers
- **Task**: Individual tasks with colors, deadlines, and descriptions
- **Comment**: Task discussion comments
- **Friend**: User friendship relationships

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
1. Check the existing issues in the GitHub repository
2. Create a new issue with detailed information about your problem
3. Include steps to reproduce the issue and any error messages

## Roadmap

- [ ] Real-time notifications
- [ ] Task templates
- [ ] Advanced search and filtering
- [ ] Mobile app development
- [ ] API endpoints for third-party integrations
- [ ] Advanced reporting and analytics
- [ ] Dark mode theme
- [ ] Export/import functionality
