import os
import sys
import logging
import difflib
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
                if 'function' in patch.lower() or 'def ' in patch or 'function ' in patch:
                    changes.append("Function changes")
                if 'class' in patch.lower() or 'class ' in patch:
                    changes.append("Class changes")
                if 'api' in patch.lower() or 'endpoint' in patch.lower():
                    changes.append("API changes")
                if 'ui' in patch.lower() or 'html' in patch.lower() or 'css' in patch.lower() or 'js' in patch.lower():
                    changes.append("UI changes")
                if 'bug' in patch.lower() or 'fix' in patch.lower():
                    changes.append("Bug fixes")
                if 'test' in patch.lower():
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

def format_release_notes(commit_info, changes, analysis_summary):
    """Format the release notes in the specified format."""
    logger.info("Formatting release notes")
    notes = []
    notes.append("Release Notes")
    notes.append("=============\n")

    notes.append(f"🗓️ Date: {commit_info['date']} at {commit_info['time']}")
    notes.append(f"👤 Author: {commit_info['author']}\n")

    # Add file changes
    for file in changes['files']:
        if file.status == 'added':
            notes.append(f"- Created: New file `{file.filename}`")
        elif file.status == 'modified':
            notes.append(f"- Modified: `{file.filename}`")
        elif file.status == 'removed':
            notes.append(f"- Deleted: `{file.filename}`")

    # Add detailed analysis
    notes.append("\n📝 Detailed Analysis:")
    notes.append(analysis_summary)
    notes.append("\n" + "="*50 + "\n")

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

        # Analyze changes
        analysis_summary = analyze_changes_with_ai(changes)

        # Format release notes
        new_content = format_release_notes(commit_info, changes, analysis_summary)

        # Update the file
        update_release_notes(new_content)

        logger.info("Release notes generation completed successfully")
    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
