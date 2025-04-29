import os
import sys
from datetime import datetime
from github import Github
import openai
from pathlib import Path

# Initialize GitHub client
github_token = os.environ.get('GITHUB_TOKEN')
g = Github(github_token)

# Initialize OpenAI client
openai.api_key = os.environ.get('OPENAI_API_KEY')

def get_repository():
    """Get the current repository from GitHub Actions environment."""
    github_repository = os.environ.get('GITHUB_REPOSITORY')
    return g.get_repo(github_repository)

def get_commit_info(repo, commit_sha):
    """Get commit information including author and date."""
    commit = repo.get_commit(commit_sha)
    return {
        'author': commit.author.login if commit.author else 'Unknown',
        'date': commit.commit.author.date.strftime('%Y-%m-%d'),
        'message': commit.commit.message
    }

def get_changes(repo, base_sha, head_sha):
    """Get the diff between two commits."""
    comparison = repo.compare(base_sha, head_sha)
    return {
        'files': comparison.files,
        'commits': comparison.commits
    }

def analyze_changes_with_ai(changes):
    """Use OpenAI to analyze and summarize code changes."""
    prompt = f"""Analyze these code changes and provide a clear, concise summary:
    Files changed: {[f.filename for f in changes['files']]}
    Number of commits: {len(changes['commits'])}

    Please summarize the major changes in simple language, focusing on:
    1. New features or functionality added
    2. Bug fixes or improvements
    3. API changes
    4. Important refactoring
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a technical writer who creates clear, concise summaries of code changes."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def format_release_notes(commit_info, changes, ai_summary):
    """Format the release notes in the specified format."""
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

    return "\n".join(notes)

def update_release_notes(new_content):
    """Update the release_note.txt file, adding new content at the top."""
    file_path = Path('release_note.txt')

    # Read existing content if file exists
    existing_content = ""
    if file_path.exists():
        with open(file_path, 'r') as f:
            existing_content = f.read()

    # Write new content at the top
    with open(file_path, 'w') as f:
        f.write(new_content + "\n\n" + existing_content)

def main():
    repo = get_repository()

    # Get the current and previous commit SHAs
    current_sha = os.environ.get('GITHUB_SHA')
    base_sha = f"{current_sha}^"  # Previous commit

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

if __name__ == "__main__":
    main()
