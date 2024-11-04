#!/usr/bin/env python3
import click
import datetime
import json
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional

class Category(Enum):
    PRODUCT_DEV = "Product dev"
    SWARM_SUPPORT = "Swarm Support"
    INTERNAL_TECH = "Internal Tech"
    SALES = "Sales"
    MARKETING = "Marketing"
    ADMIN_COORD = "Admin & Coord"
    OTHER = "Other"

class TimeTracker:
    def __init__(self):
        self.data_file = Path.home() / '.timetrack_data.json'
        self.categories_file = Path.home() / '.timetrack_categories.json'
        self.categories = self._load_categories()
        self.active_timers = self._load_active_timers()
        self.sessions = self._load_sessions()

    def _load_categories(self):
        """Load categories from JSON file or return defaults."""
        if self.categories_file.exists():
            with open(self.categories_file) as f:
                return json.load(f)
        
        # Default categories if no file exists
        default_categories = {
            "Product dev": ["Software development", "SysAdmin for products", "Tech check-in for development"],
            "Swarm Support": ["Tech support", "Tech maintenance", "Communication", "Administration", "Coordination"],
            "Internal Tech": ["Support", "Galaxy", "Homepage development", "SysAdmin", "Tech Coordination", "Tech check-in SysAdmin"],
            "Sales": ["Direct sales", "Sales meetings/calls", "CRM work", "Customer research", "Marketing & Sales Meeting"],
            "Marketing": ["Branding", "Campaigns", "Social media", "Homepage maintenance", "Design", "Marketing & Sales Meeting"],
            "Admin & Coord": ["Financial", "Administration", "Legal", "Planning", "Board", "Quality management", 
                            "Coordination meetings", "General communication", "General Sprint meetings"],
            "Other": ["MetaLand", "Other Other"]
        }
        
        # Save default categories to file
        with open(self.categories_file, 'w') as f:
            json.dump(default_categories, f, indent=2)
        
        return default_categories

    def _load_active_timers(self):
        if self.data_file.exists():
            with open(self.data_file) as f:
                data = json.load(f)
                return data.get('active_timers', {})
        return {}

    def _load_sessions(self):
        if self.data_file.exists():
            with open(self.data_file) as f:
                data = json.load(f)
                return data.get('sessions', [])
        return []

    def _save_data(self):
        data = {
            'active_timers': self.active_timers,
            'sessions': self.sessions
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, default=str)

    def get_subcategories(self, main_category: str) -> List[str]:
        return self.categories.get(main_category, [])

    def start_timer(self, main_category: str, subcategory: str, description: str = ""):
        if not subcategory in self.get_subcategories(main_category):
            valid_subcategories = "\n".join(f"- {sub}" for sub in self.get_subcategories(main_category))
            raise click.ClickException(
                f"Invalid subcategory! Valid subcategories for {main_category} are:\n{valid_subcategories}"
            )

        # Check if any active timers are already running
        if self.active_timers:
            click.echo("A timer is already active:")
            for timer_key, timer_data in self.active_timers.items():
                click.echo(f" - {timer_key} running since {timer_data['start_time']}")

            # Ask the user if they want to stop the current timer
            if click.confirm("Do you want to stop the current timer before starting a new one?", default=True):
                # Stop the active timers
                for timer_key in list(self.active_timers.keys()):
                    self.end_timer(
                        self.active_timers[timer_key]['main_category'],
                        self.active_timers[timer_key]['subcategory']
                    )
            else:
                raise click.ClickException("Please stop the current timer before starting a new one.")

        timer_key = f"{main_category} - {subcategory}"
        self.active_timers[timer_key] = {
            'start_time': datetime.datetime.now(),
            'main_category': main_category,
            'subcategory': subcategory,
            'description': description
        }
        self._save_data()
        click.echo(f"Started timer for '{timer_key}' - {description}")
        
    def prompt_category_selection(self) -> tuple[str, str, str]:
        """Interactive wizard for category selection."""
        # Display main categories
        click.echo("\nAvailable categories:")
        categories = list(self.categories.keys())
        for idx, category in enumerate(categories, 1):
            click.echo(f"{idx}. {category}")
        
        # Get main category selection
        while True:
            try:
                category_idx = click.prompt(
                    "Select category number",
                    type=int,
                    prompt_suffix=": "
                )
                if 1 <= category_idx <= len(categories):
                    main_category = categories[category_idx - 1]
                    break
                click.echo("Invalid selection. Please choose a valid number.")
            except ValueError:
                click.echo("Please enter a valid number.")
        
        # Display subcategories
        subcategories = self.get_subcategories(main_category)
        click.echo(f"\nAvailable subcategories for {main_category}:")
        for idx, subcategory in enumerate(subcategories, 1):
            click.echo(f"{idx}. {subcategory}")
        
        # Get subcategory selection
        while True:
            try:
                subcategory_idx = click.prompt(
                    "Select subcategory number",
                    type=int,
                    prompt_suffix=": "
                )
                if 1 <= subcategory_idx <= len(subcategories):
                    subcategory = subcategories[subcategory_idx - 1]
                    break
                click.echo("Invalid selection. Please choose a valid number.")
            except ValueError:
                click.echo("Please enter a valid number.")
        
        # Optional description
        description = click.prompt(
            "Enter task description (optional - press Enter to skip)",
            type=str,
            default="",
            show_default=False
        )
        
        return main_category, subcategory, description

    def start_timer_wizard(self):
        """Start a timer using an interactive wizard."""
        main_category, subcategory, description = self.prompt_category_selection()
        self.start_timer(main_category, subcategory, description)

    def end_timer(self, main_category: Optional[str] = None, subcategory: Optional[str] = None):
        if not self.active_timers:
            raise click.ClickException("No active timers!")

        timer_key = None
        if main_category and subcategory:
            timer_key = f"{main_category} - {subcategory}"
        elif len(self.active_timers) == 1:
            timer_key = list(self.active_timers.keys())[0]
        else:
            raise click.ClickException("Multiple timers active. Please specify category and subcategory.")

        if timer_key not in self.active_timers:
            raise click.ClickException(f"No active timer found for '{timer_key}'")

        timer_data = self.active_timers[timer_key]
        end_time = datetime.datetime.now()
        start_time = datetime.datetime.fromisoformat(str(timer_data['start_time']))
        duration = end_time - start_time

        session = {
            'id': len(self.sessions) + 1,  # Add unique id
            'main_category': timer_data['main_category'],
            'subcategory': timer_data['subcategory'],
            'description': timer_data['description'],
            'start_time': start_time,
            'end_time': end_time,
            'duration': str(duration),
            'duration_hours': duration.total_seconds() / 3600,
            'week': start_time.isocalendar()[1]
        }

        self.sessions.append(session)
        del self.active_timers[timer_key]
        self._save_data()

        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        click.echo(f"Ended timer for '{timer_key}'")
        click.echo(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def prompt_session_selection(self) -> int:
        """Interactive wizard for selecting a session to edit."""
        if not self.sessions:
            raise click.ClickException("No sessions available to edit")
        
        click.echo("\nAvailable sessions:")
        for session in self.sessions:
            click.echo(f"ID: {session['id']} - {session['main_category']} - {session['subcategory']} ({session['duration_hours']:.2f}h)")
        
        while True:
            try:
                session_id = click.prompt("Select session ID to edit", type=int)
                if any(s['id'] == session_id for s in self.sessions):
                    return session_id
                click.echo("Invalid session ID. Please try again.")
            except ValueError:
                click.echo("Please enter a valid number.")

    def edit_session_wizard(self):
        """Interactive wizard for editing a session."""
        session_id = self.prompt_session_selection()
        duration_hours = click.prompt("Enter new duration in hours", type=float)
        return self.edit_session(session_id, duration_hours)

    def edit_session(self, session_id: int, duration_hours: float):
        """Edit a session's duration."""
        session = next((s for s in self.sessions if s['id'] == session_id), None)
        if not session:
            raise click.ClickException(f"No session found with id {session_id}")
        
        # Update duration and related fields
        session['duration_hours'] = duration_hours
        duration_delta = datetime.timedelta(hours=duration_hours)
        session['duration'] = str(duration_delta)
        
        # Convert start_time to datetime if it's a string
        if isinstance(session['start_time'], str):
            session['start_time'] = datetime.datetime.fromisoformat(session['start_time'])
        
        # Calculate new end time
        session['end_time'] = session['start_time'] + duration_delta
        
        self._save_data()
        return session

    def remove_session(self, session_id: int) -> bool:
        """Remove a single session by ID."""
        session = next((s for s in self.sessions if s['id'] == session_id), None)
        if not session:
            raise click.ClickException(f"No session found with id {session_id}")
        
        self.sessions.remove(session)
        self._save_data()
        return True

    def remove_all_sessions(self) -> int:
        """Remove all sessions and return count of removed sessions."""
        count = len(self.sessions)
        self.sessions = []
        self._save_data()
        return count

    def remove_sessions_by_date(self, target_date: datetime.date) -> int:
        """Remove sessions for specific date."""
        original_count = len(self.sessions)
        self.sessions = [
            s for s in self.sessions 
            if datetime.datetime.fromisoformat(str(s['start_time'])).date() != target_date
        ]
        removed_count = original_count - len(self.sessions)
        self._save_data()
        return removed_count

    def remove_sessions_by_week(self, week_offset: int = 0) -> int:
        """Remove sessions for specific week."""
        target_week = (datetime.datetime.now() + datetime.timedelta(weeks=week_offset)).isocalendar()[1]
        original_count = len(self.sessions)
        self.sessions = [s for s in self.sessions if s['week'] != target_week]
        removed_count = original_count - len(self.sessions)
        self._save_data()
        return removed_count

    def add_session(self, date: datetime.datetime, duration_hours: float, main_category: str, subcategory: str, description: str = ""):
        """Add a new session directly."""
        if not subcategory in self.get_subcategories(main_category):
            valid_subcategories = "\n".join(f"- {sub}" for sub in self.get_subcategories(main_category))
            raise click.ClickException(
                f"Invalid subcategory! Valid subcategories for {main_category} are:\n{valid_subcategories}"
            )
        
        start_time = date
        end_time = start_time + datetime.timedelta(hours=duration_hours)
        
        session = {
            'id': len(self.sessions) + 1,
            'main_category': main_category,
            'subcategory': subcategory,
            'description': description,
            'start_time': start_time,
            'end_time': end_time,
            'duration': str(datetime.timedelta(hours=duration_hours)),
            'duration_hours': duration_hours,
            'week': start_time.isocalendar()[1]
        }
        
        self.sessions.append(session)
        self._save_data()
        return session

    def add_session_wizard(self):
        """Interactive wizard for adding a new session."""
        # Get date with today as default
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        date_str = click.prompt("Enter date (YYYY-MM-DD)", type=str, default=today)
        
        # Get time with current hour as default
        current_time = datetime.datetime.now().strftime("%H:%M")
        time_str = click.prompt("Enter time (HH:MM)", type=str, default=current_time)
        
        try:
            date = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise click.ClickException("Invalid date/time format")
        
        # Default duration of 1 hour
        duration_hours = click.prompt("Enter duration in hours", type=float, default=1.0)
        
        # Get category and subcategory using existing wizard
        main_category, subcategory, description = self.prompt_category_selection()
        
        return self.add_session(date, duration_hours, main_category, subcategory, description)
    
    def generate_report(self, week: Optional[int] = None, format_type: str = "detailed"):
        if not self.sessions:
            click.echo("No sessions recorded yet!")
            return

        filtered_sessions = self.sessions
        if week is not None:
            filtered_sessions = [s for s in self.sessions if s['week'] == week]
            if not filtered_sessions:
                click.echo(f"No sessions found for week {week}")
                return

        if format_type == "summary":
            self._generate_summary_report(filtered_sessions)
        else:
            self._generate_detailed_report(filtered_sessions)

    def _generate_detailed_report(self, sessions):
        click.echo("\nDetailed Time Tracking Report")
        click.echo("-" * 100)
        click.echo(f"{'Category':<15} {'Subcategory':<20} {'Description':<25} {'Duration':<10} {'Date':<15}")
        click.echo("-" * 100)

        for session in sessions:
            start = datetime.datetime.fromisoformat(str(session['start_time']))
            duration_hours = session['duration_hours']
            click.echo(
                f"{session['main_category']:<15} "
                f"{session['subcategory']:<20} "
                f"{(session['description'][:22] + '...') if len(session['description']) > 25 else session['description']:<25} "
                f"{f'{duration_hours:.2f}h':<10} "
                f"{start.strftime('%Y-%m-%d'):<15}"
            )

    def _generate_summary_report(self, sessions):
        click.echo("\nTime Tracking Summary")
        click.echo("-" * 50)
        
        # Group by main category
        category_totals: Dict[str, float] = {}
        subcategory_totals: Dict[str, Dict[str, float]] = {}

        for session in sessions:
            main_cat = session['main_category']
            sub_cat = session['subcategory']
            duration = session['duration_hours']

            category_totals[main_cat] = category_totals.get(main_cat, 0) + duration
            
            if main_cat not in subcategory_totals:
                subcategory_totals[main_cat] = {}
            subcategory_totals[main_cat][sub_cat] = subcategory_totals[main_cat].get(sub_cat, 0) + duration

        # Print totals
        total_hours = sum(category_totals.values())
        for main_cat in Category._member_map_.values():
            main_cat = main_cat.value
            if main_cat in category_totals:
                click.echo(f"\n{main_cat}:")
                for sub_cat, hours in subcategory_totals[main_cat].items():
                    click.echo(f"  {sub_cat}: ({hours:.2f})")
                click.echo(f"Total: ({category_totals[main_cat]:.2f})")

        click.echo(f"\nTotal Hours: {total_hours:.2f}")

@click.group()
@click.pass_context
def cli(ctx):
    """Enhanced time tracking command line tool."""
    ctx.obj = TimeTracker()


@cli.command()
@click.argument('main_category', required=False)
@click.argument('subcategory', required=False)
@click.option('--description', '-d', default="", help='Optional description of the task')
@click.pass_obj
def start(tracker, main_category, subcategory, description):
    """
    Start a timer. If no category/subcategory provided, launches interactive wizard.
    
    Examples:
        timetrack start  # launches interactive wizard
        timetrack start "Product dev" "Software development" -d "Working on paywall"
    """
    if main_category is None or subcategory is None:
        tracker.start_timer_wizard()
    else:
        tracker.start_timer(main_category, subcategory, description)

@cli.command()
@click.option('--date', type=str, help='Date in YYYY-MM-DD format')
@click.option('--time', type=str, help='Time in HH:MM format')
@click.option('--duration', type=float, help='Duration in hours')
@click.option('--main-category', type=str, help='Main category')  # Changed from main_category to main-category
@click.option('--subcategory', type=str, help='Subcategory')
@click.option('--description', type=str, default="", help='Optional description')
@click.pass_obj
def add(tracker, date, time, duration, main_category, subcategory, description):
    """Add a time tracking session. If no options provided, launches interactive wizard."""
    if all([date, time, duration, main_category, subcategory]):
        try:
            datetime_obj = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise click.ClickException("Invalid date/time format")
        session = tracker.add_session(datetime_obj, duration, main_category, subcategory, description)
    else:
        session = tracker.add_session_wizard()
    
    click.echo(f"\nAdded new session {session['id']}:")
    click.echo(f"Date: {session['start_time'].strftime('%Y-%m-%d %H:%M')}")
    click.echo(f"Category: {session['main_category']} - {session['subcategory']}")
    click.echo(f"Duration: {session['duration_hours']:.2f}h")
    click.echo(f"Description: {session['description']}")


@cli.command()
@click.option('--id', 'session_id', type=int, help='Session ID to edit')
@click.option('--duration', 'duration_hours', type=float, help='New duration in hours')
@click.pass_obj
def edit(tracker, session_id, duration_hours):
    """Edit a session's duration. If no options provided, launches interactive wizard."""
    if session_id is None or duration_hours is None:
        session = tracker.edit_session_wizard()
    else:
        session = tracker.edit_session(session_id, duration_hours)
    
    click.echo(f"\nUpdated session {session['id']}:")
    click.echo(f"Category: {session['main_category']} - {session['subcategory']}")
    click.echo(f"Duration: {session['duration_hours']:.2f}h")
    click.echo(f"Description: {session['description']}")

@cli.command()
@click.option('--id', type=int, help='Remove session by ID')
@click.option('--all', 'remove_all', is_flag=True, help='Remove all sessions')
@click.option('--day', type=int, is_flag=False, flag_value=0, help='Remove sessions by day offset (0=today, -1=yesterday)')
@click.option('--week', type=int, help='Remove sessions by week offset (0=this week, -1=last week)')
@click.pass_obj
def remove(tracker, id, remove_all, day, week):
    """Remove time tracking sessions based on specified criteria."""
    if sum(1 for x in [id, remove_all, day is not None, week is not None] if x) != 1:
        raise click.ClickException("Please specify exactly one removal option")

    if id:
        tracker.remove_session(id)
        click.echo(f"Removed session {id}")
    
    elif remove_all:
        count = tracker.remove_all_sessions()
        click.echo(f"Removed all {count} sessions")
    
    elif day is not None:
        target_date = datetime.datetime.now().date() + datetime.timedelta(days=day)
        count = tracker.remove_sessions_by_date(target_date)
        click.echo(f"Removed {count} sessions from {target_date}")
    
    elif week is not None:
        count = tracker.remove_sessions_by_week(week)
        click.echo(f"Removed {count} sessions from week offset {week}")

@cli.command()
@click.option('--main-category', '-m', help='Main category to end timer for')
@click.option('--subcategory', '-s', help='Subcategory to end timer for')
@click.pass_obj
def end(tracker, main_category, subcategory):
    """End a timer. If no category specified, ends the last started timer."""
    tracker.end_timer(main_category, subcategory)

@cli.command()
@click.option('--week', type=int, help='Filter report by week number')
@click.option('--format', 'format_type', type=click.Choice(['detailed', 'summary']), 
              default='detailed', help='Report format type')
@click.pass_obj
def report(tracker, week, format_type):
    """Generate a report of time tracking sessions."""
    tracker.generate_report(week, format_type)

@cli.command()
@click.pass_obj
def status(tracker):
    """Show currently running timers."""
    if not tracker.active_timers:
        click.echo("No active timers")
        return

    click.echo("\nActive Timers:")
    click.echo("-" * 70)
    for timer_key, timer_data in tracker.active_timers.items():
        start = datetime.datetime.fromisoformat(str(timer_data['start_time']))
        duration = datetime.datetime.now() - start
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        description = f" - {timer_data['description']}" if timer_data['description'] else ""
        click.echo(f"{timer_key}{description:<30} Running for: {hours:02d}:{minutes:02d}:{seconds:02d}")

@cli.command()
@click.argument('category')
@click.pass_obj
def list_subcategories(tracker, category):
    """List available subcategories for a main category."""
    subcategories = tracker.get_subcategories(category)
    if not subcategories:
        click.echo(f"No subcategories found for '{category}'")
        return
    
    click.echo(f"\nSubcategories for {category}:")
    for sub in subcategories:
        click.echo(f"- {sub}")

if __name__ == '__main__':
    cli()
