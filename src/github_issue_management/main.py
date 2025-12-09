"""Main entry point for GitHub Issue Management Crew."""

import sys
from github_issue_management.crew import GithubIssueManagement


def run():
    """
    Run the GitHub Issue Management crew.
    
    This function monitors new GitHub issues, labels them, assigns team members,
    and provides initial assessment comments.
    
    Prerequisites:
    - Set GITHUB_TOKEN environment variable with a GitHub personal access token
    - Token needs 'repo' scope for private repos or 'public_repo' for public repos
    - Ensure the repository has appropriate labels (bug, feature-request, documentation, etc.)
    
    Example:
        inputs = {
            "repository": "octocat/Hello-World",
            "team_members": {
                "frontend": ["alice", "bob"],
                "backend": ["charlie"],
                "devops": ["dave"],
                "documentation": ["eve"],
            },
        }
    """
    inputs = {
        "repository": "owner/repo",  # GitHub repository in format 'owner/repo'
        "team_members": {
            "frontend": ["username1", "username2"],  # Frontend experts (React, UI, CSS)
            "backend": ["username3", "username4"],  # Backend experts (API, database, server)
            "devops": ["username5"],  # DevOps experts (deployment, CI/CD, infrastructure)
            "documentation": ["username6"],  # Documentation experts
        },
    }
    
    # 환경 변수 확인
    import os
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️  Warning: GITHUB_TOKEN environment variable is not set.")
        print("Please set it before running the crew:")
        print("  export GITHUB_TOKEN=your_github_token")
        print("\nContinuing anyway...")
    
    try:
        result = GithubIssueManagement().crew().kickoff(inputs=inputs)
        print("\n" + "=" * 50)
        print("✅ Crew execution completed successfully!")
        print("=" * 50)
        return result
    except Exception as e:
        print(f"\n❌ Error running crew: {e}", file=sys.stderr)
        raise


def train():
    """
    Train the GitHub Issue Management crew.
    
    This function trains the crew using historical data to improve performance.
    """
    try:
        GithubIssueManagement().crew().train()
    except Exception as e:
        print(f"\nError training crew: {e}", file=sys.stderr)
        raise


def replay():
    """
    Replay the last execution of the GitHub Issue Management crew.
    
    This function replays the last crew execution for debugging or review.
    """
    try:
        GithubIssueManagement().crew().replay()
    except Exception as e:
        print(f"\nError replaying crew: {e}", file=sys.stderr)
        raise


def test():
    """
    Test the GitHub Issue Management crew.
    
    This function runs tests to validate the crew's functionality.
    """
    try:
        GithubIssueManagement().crew().test()
    except Exception as e:
        print(f"\nError testing crew: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    run()

