import pytest
from pathlib import Path
import json
import click
from click.testing import CliRunner
from timetrack.cli import TimeTracker, cli
import datetime

@pytest.fixture
def tracker():
    tracker = TimeTracker()
    tracker.data_file = Path("test_timetrack_data.json")
    # Clear any existing data
    tracker.active_timers = {}
    tracker.sessions = []
    return tracker

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def cleanup(tracker):
    if tracker.data_file.exists():
        tracker.data_file.unlink()
    yield
    if tracker.data_file.exists():
        tracker.data_file.unlink()

def test_start_timer(tracker):
    tracker.start_timer("Product dev", "Software development", "Test task")
    assert len(tracker.active_timers) == 1
    timer_key = "Product dev - Software development"
    assert timer_key in tracker.active_timers
    assert tracker.active_timers[timer_key]["description"] == "Test task"

def test_end_timer(tracker):
    # Clear any existing sessions
    tracker.sessions = []
    tracker.start_timer("Product dev", "Software development", "Test task")
    tracker.end_timer("Product dev", "Software development")
    assert len(tracker.active_timers) == 0
    assert len(tracker.sessions) == 1

def test_cli_start_command(runner):
    result = runner.invoke(cli, ["start", "Product dev", "Software development", "-d", "Test task"])
    assert result.exit_code == 0
    assert "Started timer" in result.output

def test_cli_end_command(runner):
    # First start a timer
    runner.invoke(cli, ["start", "Product dev", "Software development"])
    # Then end it
    result = runner.invoke(cli, ["end"])
    assert result.exit_code == 0
    assert "Ended timer" in result.output

def test_cli_status_command(runner):
    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0

def test_cli_report_command(runner):
    with runner.isolated_filesystem():
        tracker = TimeTracker()
        # Initialize an empty sessions list with the correct structure
        tracker.sessions = [{
            'main_category': 'Product dev',
            'subcategory': 'Software development',
            'description': 'Test task',
            'start_time': '2024-01-01 10:00:00',
            'end_time': '2024-01-01 11:00:00',
            'duration': '1:00:00',
            'duration_hours': 1.0,
            'week': 1
        }]
        tracker._save_data()
        
        result = runner.invoke(cli, ["report"])
        assert result.exit_code == 0
        assert "Detailed Time Tracking Report" in result.output
def test_invalid_subcategory(tracker):
    with pytest.raises(click.ClickException) as exc_info:
        tracker.start_timer("Product dev", "Invalid subcategory")
    assert "Invalid subcategory" in str(exc_info.value)

def test_multiple_sessions(tracker):
    # Clear existing sessions
    tracker.sessions = []
    
    # Start and end multiple sessions
    tracker.start_timer("Product dev", "Software development", "Task 1")
    tracker.end_timer("Product dev", "Software development")
    tracker.start_timer("Sales", "Direct sales", "Task 2")
    tracker.end_timer("Sales", "Direct sales")
    
    assert len(tracker.sessions) == 2

def test_report_generation(tracker, capsys):
    # Clear existing sessions
    tracker.sessions = []
    
    # Add a test session
    tracker.start_timer("Product dev", "Software development", "Task 1")
    tracker.end_timer("Product dev", "Software development")
    
    # Test detailed report
    tracker.generate_report(format_type="detailed")
    captured = capsys.readouterr()
    assert "Detailed Time Tracking Report" in captured.out
    
    # Test summary report
    tracker.generate_report(format_type="summary")
    captured = capsys.readouterr()
    assert "Time Tracking Summary" in captured.out

def test_edit_session(tracker):
    # Create a test session
    tracker.start_timer("Product dev", "Software development", "Test task")
    tracker.end_timer("Product dev", "Software development")
    
    # Get the session id
    session_id = tracker.sessions[0]['id']
    
    # Edit the session
    updated_session = tracker.edit_session(session_id, 3.0)
    
    assert updated_session['duration_hours'] == 3.0
    assert updated_session['duration'] == '3:00:00'

def test_edit_session_invalid_id(tracker):
    with pytest.raises(click.ClickException) as exc_info:
        tracker.edit_session(999, 3.0)
    assert "No session found with id 999" in str(exc_info.value)

def test_cli_edit_command(runner):
    with runner.isolated_filesystem():
        # First create a session
        tracker = TimeTracker()
        tracker.sessions = [{
            'id': 1,
            'main_category': 'Product dev',
            'subcategory': 'Software development',
            'description': 'Test task',
            'start_time': datetime.datetime(2024, 1, 1, 10, 0, 0),  # Use datetime object
            'end_time': datetime.datetime(2024, 1, 1, 11, 0, 0),    # Use datetime object
            'duration': '1:00:00',
            'duration_hours': 1.0,
            'week': 1
        }]
        tracker._save_data()
        
        result = runner.invoke(cli, ["edit", "--id", "1", "--duration", "3.0"])
        assert result.exit_code == 0
        assert "Updated session 1" in result.output
        assert "3.00h" in result.output

def test_cli_edit_wizard(runner):
    with runner.isolated_filesystem():
        # Setup test data
        tracker = TimeTracker()
        tracker.sessions = [{
            'id': 1,
            'main_category': 'Product dev',
            'subcategory': 'Software development',
            'description': 'Test task',
            'start_time': datetime.datetime(2024, 1, 1, 10, 0, 0),  # Use datetime object
            'end_time': datetime.datetime(2024, 1, 1, 11, 0, 0),    # Use datetime object
            'duration': '1:00:00',
            'duration_hours': 1.0,
            'week': 1
        }]
        tracker._save_data()
        
        # Simulate wizard input
        result = runner.invoke(cli, ["edit"], input="1\n2.5\n")
        assert result.exit_code == 0
        assert "Updated session 1" in result.output
        assert "2.50h" in result.output

def test_add_session(tracker):
    # Test direct session addition
    date = datetime.datetime(2024, 1, 1, 10, 0)
    session = tracker.add_session(
        date=date,
        duration_hours=2.0,
        main_category="Product dev",
        subcategory="Software development",
        description="Test task"
    )
    
    assert session['id'] == 1
    assert session['duration_hours'] == 2.0
    assert session['main_category'] == "Product dev"
    assert session['start_time'] == date
    assert session['end_time'] == date + datetime.timedelta(hours=2.0)

def test_cli_add_command(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(cli, [
            "add",
            "--date", "2024-01-01",
            "--time", "10:00",
            "--duration", "2.0",
            "--main_category", "Product dev",
            "--subcategory", "Software development",
            "--description", "Test task"
        ])
        assert result.exit_code == 0
        assert "Added new session" in result.output

def test_cli_add_wizard(runner):
    with runner.isolated_filesystem():
        # Simulate wizard input
        inputs = "2024-01-01\n10:00\n2.0\n1\n1\nTest task\n"
        result = runner.invoke(cli, ["add"], input=inputs)
        assert result.exit_code == 0
        assert "Added new session" in result.output
        assert "Test task" in result.output

def test_add_session_invalid_category(tracker):
    with pytest.raises(click.ClickException) as exc_info:
        tracker.add_session(
            date=datetime.datetime.now(),
            duration_hours=2.0,
            main_category="Product dev",
            subcategory="Invalid subcategory"
        )
    assert "Invalid subcategory" in str(exc_info.value)
