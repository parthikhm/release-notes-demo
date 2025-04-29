import os
import sys
import logging
import difflib
import re
from datetime import datetime
from github import Github
import openai
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize GitHub client
github_token = os.environ.get('GITHUB_TOKEN')
if not github_token:
    logger.error("GITHUB_TOKEN environment variable is not set")
    sys.exit(1)

g = Github(github_token)
logger.info("GitHub client initialized successfully")

# Initialize OpenAI client
openai_api_key = os.environ.get('OPENAI_API_KEY')
if not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    sys.exit(1)

openai.api_key = openai_api_key
logger.info("OpenAI client initialized successfully")

# Current version
CURRENT_VERSION = "1.0.0"

def get_repository():
    """Get the current repository from GitHub Actions environment."""
    github_repository = os.environ.get('GITHUB_REPOSITORY')
    if not github_repository:
        logger.error("GITHUB_REPOSITORY environment variable is not set")
        sys.exit(1)

    logger.info(f"Getting repository: {github_repository}")
    try:
        repo = g.get_repo(github_repository)
        logger.info(f"Successfully retrieved repository: {repo.full_name}")
        return repo
    except Exception as e:
        logger.error(f"Failed to get repository: {str(e)}")
        sys.exit(1)

def get_commit_info(repo, commit_sha):
    """Get commit information including author and date."""
    logger.info(f"Getting commit info for SHA: {commit_sha}")
    try:
        commit = repo.get_commit(commit_sha)
        author = commit.author.login if commit.author else 'Unknown'
        date = commit.commit.author.date.strftime('%Y-%m-%d')
        time = commit.commit.author.date.strftime('%H:%M:%S')
        logger.info(f"Commit info retrieved - Author: {author}, Date: {date}, Time: {time}")
        return {
            'author': author,
            'date': date,
            'time': time,
            'message': commit.commit.message
        }
    except Exception as e:
        logger.error(f"Failed to get commit info: {str(e)}")
        sys.exit(1)

def get_changes(repo, base_sha, head_sha):
    """Get the diff between two commits."""
    logger.info(f"Getting changes between {base_sha} and {head_sha}")
    try:
        comparison = repo.compare(base_sha, head_sha)
        # Convert PaginatedList to regular list
        files_list = list(comparison.files)
        commits_list = list(comparison.commits)
        file_count = len(files_list)
        commit_count = len(commits_list)
        logger.info(f"Retrieved {file_count} changed files and {commit_count} commits")
        return {
            'files': files_list,
            'commits': commits_list
        }
    except Exception as e:
        logger.error(f"Failed to get changes: {str(e)}")
        sys.exit(1)

def analyze_ui_changes(patch):
    """Analyze UI changes in HTML/Blade files."""
    ui_changes = []

    # Check for modal changes
    if 'modal' in patch.lower():
        if 'livewire' in patch.lower():
            if '@livewire' in patch:
                ui_changes.append("Removed Livewire component from modal")
            else:
                ui_changes.append("Added Livewire integration to modal")
        else:
            ui_changes.append("Enhanced modal functionality for better user interaction")

        # Check for form fields
        form_fields = []
        if 'input' in patch.lower():
            input_types = re.findall(r'type="([^"]*)"', patch)
            for input_type in input_types:
                if input_type not in ['hidden', 'submit', 'button']:
                    form_fields.append(input_type)

            if form_fields:
                ui_changes.append(f"Added form fields: {', '.join(form_fields)}")

        # Check for button changes
        if 'button' in patch.lower():
            button_types = re.findall(r'class="([^"]*btn[^"]*)"', patch)
            if button_types:
                ui_changes.append(f"Modified buttons: {', '.join(button_types)}")

    # Check for layout changes
    if 'container' in patch.lower() or 'row' in patch.lower() or 'col' in patch.lower():
        ui_changes.append("Improved layout structure for better content organization")

    # Check for styling changes
    if 'class="' in patch or 'style="' in patch:
        ui_changes.append("Enhanced visual styling for a more polished user experience")

    # Check for responsive design changes
    if 'media' in patch.lower() or '@media' in patch.lower():
        ui_changes.append("Improved responsive design for better mobile experience")

    # Check for accessibility improvements
    if 'aria-' in patch.lower() or 'role=' in patch.lower() or 'tabindex=' in patch.lower():
        ui_changes.append("Enhanced accessibility features for better usability")

    # Check for navigation changes
    if 'nav' in patch.lower() or 'menu' in patch.lower() or 'sidebar' in patch.lower():
        ui_changes.append("Improved navigation structure for easier site exploration")

    # Check for card or panel changes
    if 'card' in patch.lower() or 'panel' in patch.lower():
        ui_changes.append("Enhanced content presentation with improved card design")

    # Check for table changes
    if 'table' in patch.lower() or 'thead' in patch.lower() or 'tbody' in patch.lower():
        ui_changes.append("Improved data presentation with enhanced table layout")

    return ui_changes

def determine_version_increment(changes):
    """Determine how to increment the version based on the type of changes."""
    major_increment = False
    minor_increment = False
    patch_increment = False

    # Check for breaking changes (MAJOR version increment)
    for file in changes['files']:
        if file.status == 'modified':
            patch = file.patch if hasattr(file, 'patch') else ""

            # Check for API breaking changes
            if 'api' in patch.lower() and ('remove' in patch.lower() or 'delete' in patch.lower()):
                major_increment = True
                break

            # Check for database schema changes
            if 'migration' in file.filename.lower() and 'create' in patch.lower():
                major_increment = True
                break

    # Check for new features (MINOR version increment)
    if not major_increment:
        for file in changes['files']:
            if file.status == 'added' or file.status == 'modified':
                patch = file.patch if hasattr(file, 'patch') else ""

                # Check for new functions
                if '+' in patch and ('function' in patch.lower() or 'def ' in patch or 'function ' in patch):
                    function_matches = re.findall(r'^\+\s*(?:function|def)\s+([a-zA-Z0-9_]+)', patch, re.MULTILINE)
                    if function_matches:
                        minor_increment = True
                        break

                # Check for new routes
                if file.filename.endswith(('.php', '.routes.php')) and '+' in patch:
                    route_matches = re.findall(r'^\+\s*Route::(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]', patch, re.MULTILINE)
                    if route_matches:
                        minor_increment = True
                        break

    # If no major or minor changes, increment patch
    if not major_increment and not minor_increment:
        patch_increment = True

    return major_increment, minor_increment, patch_increment

def increment_version(version, major_increment, minor_increment, patch_increment):
    """Increment the version number based on the type of changes."""
    major, minor, patch = map(int, version.split('.'))

    if major_increment:
        major += 1
        minor = 0
        patch = 0
    elif minor_increment:
        minor += 1
        patch = 0
    elif patch_increment:
        patch += 1

    return f"{major}.{minor}.{patch}"

def analyze_file_changes(file):
    """Analyze changes in a specific file."""
    try:
        # Get the file content before and after the change
        if hasattr(file, 'raw_url'):
            # For added files, we only have the new content
            if file.status == 'added':
                return {
                    'status': 'added',
                    'filename': file.filename,
                    'changes': 'New file added',
                    'additions': file.additions,
                    'deletions': 0
                }

            # For modified files, we need to get the diff
            elif file.status == 'modified':
                # Get the patch to analyze the changes
                patch = file.patch if hasattr(file, 'patch') else "No patch available"

                # Count the number of additions and deletions
                additions = file.additions
                deletions = file.deletions

                # Try to determine what kind of changes were made
                changes = []

                # Check for UI changes in HTML/Blade files
                if file.filename.endswith(('.html', '.blade.php', '.vue', '.jsx', '.tsx')):
                    ui_changes = analyze_ui_changes(patch)
                    if ui_changes:
                        changes.extend(ui_changes)

                # Check for new functions created
                new_functions = []
                if '+' in patch and ('function' in patch.lower() or 'def ' in patch or 'function ' in patch):
                    # Look for function definitions with + at the start of the line
                    function_matches = re.findall(r'^\+\s*(?:function|def)\s+([a-zA-Z0-9_]+)', patch, re.MULTILINE)
                    if function_matches:
                        new_functions.extend(function_matches)

                if new_functions:
                    changes.append(f"Created new functions: {', '.join(new_functions)}")

                # Check for new routes created (for Laravel/PHP files)
                new_routes = []
                if file.filename.endswith(('.php', '.routes.php')) and '+' in patch:
                    # Look for route definitions with + at the start of the line
                    route_matches = re.findall(r'^\+\s*Route::(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]', patch, re.MULTILINE)
                    if route_matches:
                        for method, path in route_matches:
                            new_routes.append(f"{method.upper()} {path}")

                if new_routes:
                    changes.append(f"Created new routes: {', '.join(new_routes)}")

                # Check for specific function changes (existing functions modified)
                if 'function' in patch.lower() or 'def ' in patch or 'function ' in patch:
                    # Extract function names if possible
                    function_names = re.findall(r'(?:function|def)\s+([a-zA-Z0-9_]+)', patch)
                    if function_names:
                        changes.append(f"Modified functions: {', '.join(function_names)}")
                    else:
                        changes.append("Function changes")

                # Check for specific class changes
                if 'class' in patch.lower() or 'class ' in patch:
                    # Extract class names if possible
                    class_names = re.findall(r'class\s+([a-zA-Z0-9_]+)', patch)
                    if class_names:
                        changes.append(f"Modified classes: {', '.join(class_names)}")
                    else:
                        changes.append("Class changes")

                # Check for API changes
                if 'api' in patch.lower() or 'endpoint' in patch.lower():
                    # Extract endpoint paths if possible
                    endpoints = re.findall(r'(?:api|endpoint)[/:]([a-zA-Z0-9_/]+)', patch)
                    if endpoints:
                        changes.append(f"Modified API endpoints: {', '.join(endpoints)}")
                    else:
                        changes.append("API changes")

                # Check for bug fixes
                if 'bug' in patch.lower() or 'fix' in patch.lower():
                    # Try to extract bug description if possible
                    bug_descriptions = re.findall(r'(?:bug|fix)[:\s]+([a-zA-Z0-9_\s]+)', patch)
                    if bug_descriptions:
                        changes.append(f"Fixed bugs: {', '.join(bug_descriptions)}")
                    else:
                        changes.append("Bug fixes")

                # Check for test changes
                if 'test' in patch.lower():
                    # Extract test names if possible
                    test_names = re.findall(r'test_([a-zA-Z0-9_]+)', patch)
                    if test_names:
                        changes.append(f"Modified tests: {', '.join(test_names)}")
                    else:
                        changes.append("Test changes")

                # If no specific changes were detected, provide a generic message
                if not changes:
                    changes = ["Code modifications"]

                return {
                    'status': 'modified',
                    'filename': file.filename,
                    'changes': ", ".join(changes),
                    'additions': additions,
                    'deletions': deletions,
                    'patch': patch
                }

            # For removed files, we only know it was deleted
            elif file.status == 'removed':
                return {
                    'status': 'removed',
                    'filename': file.filename,
                    'changes': 'File removed',
                    'additions': 0,
                    'deletions': file.deletions
                }

        # Fallback for files without raw_url
        return {
            'status': file.status,
            'filename': file.filename,
            'changes': f"File {file.status}",
            'additions': getattr(file, 'additions', 0),
            'deletions': getattr(file, 'deletions', 0)
        }
    except Exception as e:
        logger.error(f"Error analyzing file {file.filename}: {str(e)}")
        return {
            'status': file.status,
            'filename': file.filename,
            'changes': f"Error analyzing changes: {str(e)}",
            'additions': 0,
            'deletions': 0
        }

def analyze_changes_with_ai(changes):
    """Analyze code changes and generate a detailed summary."""
    logger.info("Analyzing code changes")
    try:
        # Analyze each file's changes
        file_analyses = []
        for file in changes['files']:
            analysis = analyze_file_changes(file)
            file_analyses.append(analysis)

        # Group files by status
        added_files = [f for f in file_analyses if f['status'] == 'added']
        modified_files = [f for f in file_analyses if f['status'] == 'modified']
        removed_files = [f for f in file_analyses if f['status'] == 'removed']

        # Generate a detailed summary
        summary = []

        # Summary of added files
        if added_files:
            summary.append("Added Files:")
            for file in added_files:
                summary.append(f"- {file['filename']}")

        # Summary of modified files
        if modified_files:
            summary.append("\nModified Files:")
            for file in modified_files:
                summary.append(f"- {file['filename']}: {file['changes']} (+{file['additions']}/-{file['deletions']} lines)")

        # Summary of removed files
        if removed_files:
            summary.append("\nRemoved Files:")
            for file in removed_files:
                summary.append(f"- {file['filename']}")

        # Add a general summary
        total_additions = sum(f['additions'] for f in file_analyses)
        total_deletions = sum(f['deletions'] for f in file_analyses)
        summary.append(f"\nTotal Changes: {len(file_analyses)} files changed, {total_additions} additions, {total_deletions} deletions")

        return "\n".join(summary)
    except Exception as e:
        logger.error(f"Failed to analyze changes: {str(e)}")
        return "Unable to generate detailed summary due to an error."

def format_release_notes(commit_info, changes, analysis_summary, version):
    """Format the release notes in the specified format."""
    logger.info("Formatting release notes")

    # Get current month and year
    current_date = datetime.now()
    month_year = current_date.strftime("%B %Y")

    # Extract version components
    major, minor, patch = map(int, version.split('.'))

    # Create the release notes
    notes = []

    # Header with month and version
    notes.append(f"{month_year} (version {major}.{minor})")
    notes.append("-" * 69)
    notes.append("")

    # Add patch updates if there are any
    if patch > 0:
        for p in range(1, patch + 1):
            notes.append(f"Update {major}.{minor}.{p}: The update addresses these issues.")
            notes.append("")

    # Welcome message
    notes.append(f"Welcome to the {month_year} release of Your Application. There are many updates in this version that we hope you'll like, some of the key highlights include:")
    notes.append("")

    # Categorize changes
    ui_changes = []
    feature_changes = []
    bug_fixes = []
    api_changes = []
    other_changes = []

    # Analyze changes to categorize them
    for file in changes['files']:
        if file.status == 'modified':
            patch = file.patch if hasattr(file, 'patch') else ""

            # UI changes
            if file.filename.endswith(('.html', '.blade.php', '.vue', '.jsx', '.tsx', '.css', '.scss')):
                # Get the base filename without path
                base_filename = os.path.basename(file.filename)

                # Check for specific UI components
                if 'modal' in patch.lower():
                    ui_changes.append(f"Enhanced modal functionality in {base_filename} for improved user interaction")
                elif 'button' in patch.lower():
                    ui_changes.append(f"Improved button design and functionality in {base_filename}")
                elif 'form' in patch.lower():
                    ui_changes.append(f"Enhanced form elements in {base_filename} for better data entry")
                elif 'style' in patch.lower() or 'class' in patch.lower():
                    ui_changes.append(f"Refined visual styling in {base_filename} for a more polished look")
                elif 'layout' in patch.lower() or 'container' in patch.lower():
                    ui_changes.append(f"Redesigned layout in {base_filename} for better content organization")
                elif 'responsive' in patch.lower() or 'media' in patch.lower():
                    ui_changes.append(f"Improved responsive design in {base_filename} for better mobile experience")
                elif 'accessibility' in patch.lower() or 'aria-' in patch.lower():
                    ui_changes.append(f"Enhanced accessibility features in {base_filename} for better usability")
                elif 'table' in patch.lower():
                    ui_changes.append(f"Improved data presentation in {base_filename} with enhanced table layout")
                else:
                    ui_changes.append(f"Enhanced user interface in {base_filename} for better user experience")

            # Feature changes
            if '+' in patch and ('function' in patch.lower() or 'def ' in patch or 'function ' in patch):
                function_matches = re.findall(r'^\+\s*(?:function|def)\s+([a-zA-Z0-9_]+)', patch, re.MULTILINE)
                if function_matches:
                    feature_changes.append(f"Added new functions in {file.filename}: {', '.join(function_matches)}")

            # API changes
            if 'api' in patch.lower() or 'endpoint' in patch.lower():
                if 'format' in patch.lower() or 'response' in patch.lower():
                    api_changes.append(f"Improved API response formatting in {file.filename}")
                elif 'error' in patch.lower() or 'exception' in patch.lower():
                    api_changes.append(f"Enhanced error handling in {file.filename}")
                else:
                    api_changes.append(f"Modified API in {file.filename}")

            # Bug fixes
            if 'bug' in patch.lower() or 'fix' in patch.lower():
                bug_fixes.append(f"Fixed issues in {file.filename}")

            # Other changes
            if not any([ui_changes, feature_changes, api_changes, bug_fixes]):
                other_changes.append(f"Updated {file.filename}")

    # Add categorized sections with emojis
    if ui_changes:
        notes.append("✨ User Interface")
        for change in ui_changes:
            notes.append(f"- {change}")
        notes.append("")

    if feature_changes:
        notes.append("🚀 New Features")
        for change in feature_changes:
            notes.append(f"- {change}")
        notes.append("")

    if api_changes:
        notes.append("🛠️ API Enhancements")
        for change in api_changes:
            notes.append(f"- {change}")
        notes.append("")

    if bug_fixes:
        notes.append("🐞 Bug Fixes")
        for change in bug_fixes:
            notes.append(f"- {change}")
        notes.append("")

    if other_changes:
        notes.append("📝 Other Updates")
        for change in other_changes:
            notes.append(f"- {change}")
        notes.append("")

    # Add footer with version and date
    notes.append("-" * 69)
    notes.append(f"Version: {version} | Date: {commit_info['date']} at {commit_info['time']} | Author: {commit_info['author']}")

    formatted_notes = "\n".join(notes)
    logger.info("Release notes formatted successfully")
    return formatted_notes

def update_release_notes(new_content):
    """Update the release_note.txt file, adding new content at the top."""
    file_path = Path('release_note.txt')
    logger.info(f"Updating release notes file: {file_path.absolute()}")

    try:
        # Read existing content if file exists
        existing_content = ""
        if file_path.exists():
            with open(file_path, 'r') as f:
                existing_content = f.read()
            logger.info("Read existing release notes content")

        # Write new content at the top
        with open(file_path, 'w') as f:
            f.write(new_content + "\n\n" + existing_content)
        logger.info("Successfully updated release_note.txt")

        # Verify the file was created
        if file_path.exists():
            file_size = file_path.stat().st_size
            logger.info(f"Release notes file exists with size: {file_size} bytes")
        else:
            logger.error("Release notes file was not created")
    except Exception as e:
        logger.error(f"Failed to update release notes file: {str(e)}")
        sys.exit(1)

def main():
    logger.info("Starting release notes generation")

    try:
        repo = get_repository()

        # Get the current and previous commit SHAs
        current_sha = os.environ.get('GITHUB_SHA')
        if not current_sha:
            logger.error("GITHUB_SHA environment variable is not set")
            sys.exit(1)

        base_sha = f"{current_sha}^"  # Previous commit
        logger.info(f"Current SHA: {current_sha}, Base SHA: {base_sha}")

        # Get commit information
        commit_info = get_commit_info(repo, current_sha)

        # Get changes
        changes = get_changes(repo, base_sha, current_sha)

        # Determine version increment
        major_increment, minor_increment, patch_increment = determine_version_increment(changes)
        new_version = increment_version(CURRENT_VERSION, major_increment, minor_increment, patch_increment)
        logger.info(f"Version increment: {CURRENT_VERSION} -> {new_version}")

        # Analyze changes
        analysis_summary = analyze_changes_with_ai(changes)

        # Format release notes
        new_content = format_release_notes(commit_info, changes, analysis_summary, new_version)

        # Update the file
        update_release_notes(new_content)

        logger.info("Release notes generation completed successfully")
    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
