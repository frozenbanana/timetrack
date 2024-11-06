# TimeTrack CLI

A simple command-line time tracking tool for managing and reporting work activities across different categories.

## Features

- Interactive wizards for easy time tracking
- Flexible category and subcategory system
- Detailed and summary reporting
- Session editing and management
- Multiple timer support
- Persistent data storage

## Categories
Default categories include:

-  Product dev
-  Swarm Support
-  Internal Tech
-  Sales
-  Marketing
-  Admin & Coord
-  Other

Each category has predefined subcategories that can be customized via `.timetrack_categories.json`.

## Data Storage
TimeTrack stores data in your home directory:

- `.timetrack_data.json`: Sessions and active timers
- `.timetrack_categories.json`: Category configurations


## Installation
Clone the repository and run the installation script:

```bash
./install.sh
```
This will:
1. Build the timetrack executable
2. Install it to /usr/local/bin
3. Make it available system-wide

## Quick start

**Start a new time tracking session**

`timetrack start`

**Start a session with a specific category**

`timetrack start --category "Development"`

**Start a session with category and subcategory**

`timetrack start --category "Development" --subcategory "Frontend"`

**Pause current active session**

`timetrack pause`

**Resume current active session**

`timetrack resume`

**Add past session**

`timetrack add`

**Stop the current session**

`timetrack stop`

**View today's summary**

`timetrack report today`

**View weekly summary**

`timetrack report week`

**List all active timers**

`timetrack list`

**Edit a session**

`timetrack edit <session-id>`

**Delete a session**

`timetrack delete <session-id>`


## Basic Commands

- `timetrack start`: Begin a new time tracking session
- `timetrack stop`: End the current session
- `timetrack resume`: Resume a paused session
- `timetrack status`: Show current tracking status
- `timetrack report`: Generate time tracking reports
- `timetrack categories`: Manage tracking categories

For more detailed information, run:

timetrack --help


## License
MIT License
