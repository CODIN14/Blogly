# BLOGLITE Design Documentation

This document outlines the design aspects of the BLOGLITE app, including feature descriptions and monitoring setup.

## Initial App Setup (User Authentication, Posts, Categories)

### Overview
- **Purpose**: The initial setup includes user authentication (signup, login, logout), post creation, and category filtering on the Home page.
- **Pages**:
  - **Home Page (`/home`)**: Displays recent posts with snippets, category filter, and navigation bar.
  - **Signup Page (`/sign-up`)**: Form for creating a new account with email confirmation.
  - **Login Page (`/login`)**: Form for logging in.
  - **Create Post Page (`/create-post`)**: Form for creating a new post with title, content, and category selection.

### Design Description
- **Home Page**: Features a navigation bar with links to Home, Create Post, Notifications, Profile, and Logout. Includes a category filter dropdown above a list of post snippets, each showing the username, title, truncated content, and a "Read More" link.
- **Signup Page**: Displays a form with fields for email, username, password, and confirm password, with a "Sign Up" button.
- **Login Page**: Displays a form with fields for email and password, with a "Login" button.
- **Create Post Page**: Displays a form with fields for title, content (textarea), and category (dropdown), with a "Submit Post" button.

## Profile Pictures

### Overview
- **Purpose**: Users can upload a profile picture during signup or update it later, which is displayed next to their posts and on their profile page.
- **Pages**:
  - **Home Page (`/home`)**: Profile picture (or default icon) displayed next to each post snippet.
  - **Full Post View (`/post/<id>`)**: Profile picture displayed next to the post.
  - **User Profile Page (`/posts/<username>`)**: Profile picture displayed at the top of the user’s profile.

### Design Description
- **Profile Picture Display**: On the Home page, full post view, and user profile page, a circular profile picture (or default user icon if none uploaded) is displayed to the left of the username and post content.

## Rich Text Editor with TinyMCE

### Overview
- **Purpose**: Integrated TinyMCE as a rich text editor for creating and editing posts, allowing users to format text, insert images, links, tables, and more.
- **Pages**:
  - **Create Post Page (`/create-post`)**: Replaced the plain textarea with TinyMCE editor.
  - **Edit Post Page (`/edit/<id>`)**: Replaced the plain textarea with TinyMCE editor.

### Design Description
- **Create/Edit Post Page**: The form includes a title input, a TinyMCE editor (with toolbar for formatting, image insertion, etc.), a category dropdown, and a "Submit Post" or "Update Post" button.

## AJAX Likes and Comments

### Overview
- **Purpose**: Prevent page reloads when liking or commenting on posts using AJAX, with visual feedback for like/unlike states.
- **Pages**:
  - **Home Page (`/home`)**: Like button updates count dynamically; comments are not directly added here but are visible in snippets.
  - **Full Post View (`/post/<id>`)**: Like button updates count dynamically; comment form adds comments without reload.
  - **User Profile Page (`/posts/<username>`)**: Same functionality as the full post view.
- **Styling**:
  - Like button turns blue and bold when liked, with a light background highlight; reverts to gray when unliked.

### Design Description
- **Home Page and Full Post View**: Like button (thumbs-up icon with count) and comment form (input field and "Comment" button) are displayed below each post. Comments appear dynamically below the post without reloading.

## Post Sharing

### Overview
- **Purpose**: Allow users to share posts via a link or with another user in the app.
- **Pages**:
  - **Home Page (`/home`)**: Share button on each post opens a modal.
  - **Full Post View (`/post/<id>`)**: Share button on the post opens a modal.
  - **User Profile Page (`/posts/<username>`)**: Share button on each post opens a modal.
- **Modal**:
  - Displays a shareable link with a "Copy" button.
  - Includes an input to share with another user (with autocomplete) and a "Share" button.

### Design Description
- **Home Page and Full Post View**: Share button (share icon with "Share" text) opens a modal with a shareable link (text input with "Copy" button) and a section to share with another user (input field with autocomplete and "Share" button).

## Monitoring with Grafana

### Monitoring with Grafana
- **Setup**: Grafana is configured with a Prometheus data source to monitor BLOGLITE app metrics.
- **Dashboard**: Created a "BLOGLITE Monitoring" dashboard with panels for HTTP Requests Total, HTTP Request Duration, and Post Shares Total.
- **Location**: Accessible at http://localhost:3000 (local setup).