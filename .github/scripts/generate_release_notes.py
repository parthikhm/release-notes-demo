import os
import sys
import logging
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
        logger.info(f"Commit info retrieved - Author: {author}, Date: {date}")
        return {
            'author': author,
            'date': date,
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

def analyze_changes_with_ai(changes):
    """Use OpenAI to analyze and summarize code changes."""
    logger.info("Analyzing changes with AI")
    try:
        file_names = [f.filename for f in changes['files']]
        commit_count = len(changes['commits'])

        # Create a simple summary without using OpenAI API
        summary = f"This update includes changes to {len(file_names)} files across {commit_count} commits. "

        # Add details about each file
        for file in changes['files']:
            if file.status == 'added':
                summary += f"Added new file: {file.filename}. "
            elif file.status == 'modified':
                summary += f"Modified: {file.filename}. "
            elif file.status == 'removed':
                summary += f"Removed: {file.filename}. "

        logger.info("Generated summary of changes")
        return summary
    except Exception as e:
        logger.error(f"Failed to analyze changes: {str(e)}")
        return "Unable to generate summary due to an error."

def format_release_notes(commit_info, changes, ai_summary):
    """Format the release notes in the specified format."""
    logger.info("Formatting release notes")
    notes = []
    notes.append("Release Notes")
    notes.append("=============\n")

    notes.append(f"Date: {commit_info['date']}")
    notes.append(f"Author: {commit_info['author']}\n")

    # Add file changes
    for file in changes['files']:
        if file.status == 'added':
            notes.append(f"- Created: New file `{file.filename}`")
        elif file.status == 'modified':
            notes.append(f"- Modified: `{file.filename}`")
        elif file.status == 'removed':
            notes.append(f"- Deleted: `{file.filename}`")

    # Add AI summary
    notes.append("\n📝 Summary of Changes:")
    notes.append(ai_summary)
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

        # Analyze changes with AI
        ai_summary = analyze_changes_with_ai(changes)

        # Format release notes
        new_content = format_release_notes(commit_info, changes, ai_summary)

        # Update the file
        update_release_notes(new_content)

        logger.info("Release notes generation completed successfully")
    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
