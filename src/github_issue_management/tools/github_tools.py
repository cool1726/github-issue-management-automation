"""GitHub API tools for issue management."""

import os
from typing import Type
from github import Github
from github.GithubException import GithubException
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class GetNewIssuesInput(BaseModel):
    """Input schema for GetNewIssues tool."""
    repository: str = Field(
        ...,
        description="Repository name in format 'owner/repo' (e.g., 'octocat/Hello-World')"
    )
    since: str = Field(
        default="",
        description="ISO 8601 timestamp to filter issues created after this time. If empty, returns recent issues."
    )


class GetNewIssues(BaseTool):
    """Tool to fetch new GitHub issues from a repository."""
    
    name: str = "get_new_issues"
    description: str = (
        "Fetches new GitHub issues from a specified repository. "
        "Returns a list of issues with their numbers, titles, bodies, labels, and assignees. "
        "Use this to monitor new issues that need to be processed."
    )
    args_schema: Type[BaseModel] = GetNewIssuesInput

    def _run(self, repository: str, since: str = "") -> str:
        """Fetch new issues from GitHub repository."""
        try:
            github_token = os.getenv("GITHUB_TOKEN")
            if not github_token:
                return "Error: GITHUB_TOKEN environment variable is not set."
            
            g = Github(github_token)
            repo = g.get_repo(repository)
            
            issues = repo.get_issues(state="open", sort="created", direction="desc")
            
            result = []
            for issue in issues[:20]:  # 최근 20개 이슈 확인
                if issue.pull_request:  # PR은 제외
                    continue
                
                # since 파라미터가 있으면 필터링
                if since:
                    from datetime import datetime
                    try:
                        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
                        if issue.created_at < since_dt:
                            continue
                    except ValueError:
                        pass  # Invalid since format, ignore filter
                
                issue_data = {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body or "",
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "created_at": issue.created_at.isoformat(),
                    "url": issue.html_url,
                    "state": issue.state,
                }
                
                result.append(issue_data)
            
            if not result:
                return "No new issues found."
            
            # 처리 필요한 이슈 필터링 (라벨이나 담당자가 없는 이슈)
            needs_processing = [
                item for item in result 
                if not item['labels'] or not item['assignees']
            ]
            
            output = f"Found {len(result)} open issues.\n"
            if needs_processing:
                output += f"⚠️ {len(needs_processing)} issues need processing (missing labels or assignees).\n\n"
            
            output += "\n\n".join([
                f"## Issue #{item['number']}: {item['title']}\n"
                f"**Body:** {item['body'][:300]}{'...' if len(item['body'] or '') > 300 else ''}\n"
                f"**Labels:** {', '.join(item['labels']) if item['labels'] else '❌ None'}\n"
                f"**Assignees:** {', '.join(item['assignees']) if item['assignees'] else '❌ None'}\n"
                f"**Created:** {item['created_at']}\n"
                f"**URL:** {item['url']}"
                for item in result
            ])
            
            return output
        except GithubException as e:
            return f"GitHub API Error: {str(e)}"
        except Exception as e:
            return f"Error fetching issues: {str(e)}"


class AddLabelToIssueInput(BaseModel):
    """Input schema for AddLabelToIssue tool."""
    repository: str = Field(
        ...,
        description="Repository name in format 'owner/repo'"
    )
    issue_number: int = Field(..., description="Issue number to label")
    labels: list[str] = Field(..., description="List of label names to add (e.g., ['bug', 'feature-request'])")


class AddLabelToIssue(BaseTool):
    """Tool to add labels to a GitHub issue."""
    
    name: str = "add_label_to_issue"
    description: str = (
        "Adds one or more labels to a GitHub issue. "
        "Use this to categorize issues as bug, feature-request, documentation, etc. "
        "Labels must exist in the repository."
    )
    args_schema: Type[BaseModel] = AddLabelToIssueInput

    def _run(self, repository: str, issue_number: int, labels: list[str]) -> str:
        """Add labels to a GitHub issue."""
        try:
            github_token = os.getenv("GITHUB_TOKEN")
            if not github_token:
                return "Error: GITHUB_TOKEN environment variable is not set."
            
            g = Github(github_token)
            repo = g.get_repo(repository)
            issue = repo.get_issue(issue_number)
            
            # 기존 라벨 가져오기
            existing_labels = [label.name for label in issue.labels]
            
            # 새 라벨만 추가
            labels_to_add = [label for label in labels if label not in existing_labels]
            
            if labels_to_add:
                # 라벨이 저장소에 존재하는지 확인
                repo_labels = [label.name for label in repo.get_labels()]
                invalid_labels = [label for label in labels_to_add if label not in repo_labels]
                
                if invalid_labels:
                    return f"Error: Labels {invalid_labels} do not exist in the repository. Available labels: {repo_labels[:10]}..."
                
                issue.add_to_labels(*labels_to_add)
                updated_labels = [label.name for label in issue.labels]
                return f"✅ Successfully added labels {labels_to_add} to issue #{issue_number}.\nCurrent labels: {updated_labels}"
            else:
                return f"ℹ️ All labels already exist on issue #{issue_number}.\nCurrent labels: {existing_labels}"
        except GithubException as e:
            if e.status == 404:
                return f"Error: Issue #{issue_number} not found in repository {repository}."
            elif e.status == 422:
                return f"Error: Invalid label name(s). Please check that labels exist in the repository."
            return f"GitHub API Error: {str(e)}"
        except Exception as e:
            return f"Error adding labels: {str(e)}"


class AssignIssueInput(BaseModel):
    """Input schema for AssignIssue tool."""
    repository: str = Field(..., description="Repository name in format 'owner/repo'")
    issue_number: int = Field(..., description="Issue number to assign")
    assignees: list[str] = Field(..., description="List of GitHub usernames to assign to the issue")


class AssignIssue(BaseTool):
    """Tool to assign team members to a GitHub issue."""
    
    name: str = "assign_issue"
    description: str = (
        "Assigns one or more team members to a GitHub issue. "
        "Use this to assign issues to appropriate team members based on their expertise. "
        "Usernames must be valid GitHub usernames."
    )
    args_schema: Type[BaseModel] = AssignIssueInput

    def _run(self, repository: str, issue_number: int, assignees: list[str]) -> str:
        """Assign team members to a GitHub issue."""
        try:
            github_token = os.getenv("GITHUB_TOKEN")
            if not github_token:
                return "Error: GITHUB_TOKEN environment variable is not set."
            
            g = Github(github_token)
            repo = g.get_repo(repository)
            issue = repo.get_issue(issue_number)
            
            # 기존 담당자 확인
            existing_assignees = [assignee.login for assignee in issue.assignees]
            
            # 새 담당자만 추가
            assignees_to_add = [assignee for assignee in assignees if assignee not in existing_assignees]
            
            if assignees_to_add:
                # 사용자가 저장소에 접근 가능한지 확인
                try:
                    issue.add_to_assignees(*assignees_to_add)
                    updated_assignees = [assignee.login for assignee in issue.assignees]
                    return f"✅ Successfully assigned {assignees_to_add} to issue #{issue_number}.\nCurrent assignees: {updated_assignees}"
                except GithubException as e:
                    if e.status == 422:
                        return f"Error: One or more assignees ({assignees_to_add}) may not have access to the repository or do not exist."
                    raise
            else:
                return f"ℹ️ All assignees already assigned to issue #{issue_number}.\nCurrent assignees: {existing_assignees}"
        except GithubException as e:
            if e.status == 404:
                return f"Error: Issue #{issue_number} not found in repository {repository}."
            return f"GitHub API Error: {str(e)}"
        except Exception as e:
            return f"Error assigning issue: {str(e)}"


class CommentOnIssueInput(BaseModel):
    """Input schema for CommentOnIssue tool."""
    repository: str = Field(..., description="Repository name in format 'owner/repo'")
    issue_number: int = Field(..., description="Issue number to comment on")
    comment: str = Field(..., description="Comment body in markdown format")


class CommentOnIssue(BaseTool):
    """Tool to add a comment to a GitHub issue."""
    
    name: str = "comment_on_issue"
    description: str = (
        "Adds a comment to a GitHub issue. "
        "Use this to provide initial assessment, reproduction steps, implementation suggestions, "
        "or any other feedback. Supports markdown formatting."
    )
    args_schema: Type[BaseModel] = CommentOnIssueInput

    def _run(self, repository: str, issue_number: int, comment: str) -> str:
        """Add a comment to a GitHub issue."""
        try:
            github_token = os.getenv("GITHUB_TOKEN")
            if not github_token:
                return "Error: GITHUB_TOKEN environment variable is not set."
            
            if not comment or not comment.strip():
                return "Error: Comment cannot be empty."
            
            g = Github(github_token)
            repo = g.get_repo(repository)
            issue = repo.get_issue(issue_number)
            
            # 댓글 추가
            issue.create_comment(comment)
            comment_preview = comment[:100] + "..." if len(comment) > 100 else comment
            return f"✅ Successfully added comment to issue #{issue_number}.\nComment preview: {comment_preview}"
        except GithubException as e:
            if e.status == 404:
                return f"Error: Issue #{issue_number} not found in repository {repository}."
            elif e.status == 403:
                return f"Error: Permission denied. Check that GITHUB_TOKEN has write access to issues."
            return f"GitHub API Error: {str(e)}"
        except Exception as e:
            return f"Error adding comment: {str(e)}"

