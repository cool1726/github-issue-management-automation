"""GitHub Issue Management Crew."""

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task

from github_issue_management.tools.github_tools import (
    GetNewIssues,
    AddLabelToIssue,
    AssignIssue,
    CommentOnIssue,
)

@CrewBase
class GithubIssueManagement():
    """GitHub Issue Management Crew."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def issue_monitor(self) -> Agent:
        """Agent responsible for monitoring new GitHub issues."""
        return Agent(
            config=self.agents_config["issue_monitor"],
            tools=[GetNewIssues()],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="azure/gpt-4.1", temperature=0.7),
        )

    @agent
    def labeler(self) -> Agent:
        """Agent responsible for labeling issues based on content."""
        return Agent(
            config=self.agents_config["labeler"],
            tools=[AddLabelToIssue()],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="azure/gpt-4.1", temperature=0.7),
        )

    @agent
    def assigner(self) -> Agent:
        """Agent responsible for assigning team members to issues."""
        return Agent(
            config=self.agents_config["assigner"],
            tools=[AssignIssue()],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="azure/gpt-4.1", temperature=0.7),
        )

    @agent
    def assessor(self) -> Agent:
        """Agent responsible for providing initial assessment comments."""
        return Agent(
            config=self.agents_config["assessor"],
            tools=[CommentOnIssue()],
            verbose=True,
            allow_delegation=False,
            llm=LLM(model="azure/gpt-4.1", temperature=0.7),
        )

    @task
    def monitor_issues(self) -> Task:
        """Task to monitor new GitHub issues."""
        return Task(
            config=self.tasks_config["monitor_issues"],
            markdown=False,
        )

    @task
    def label_issues(self) -> Task:
        """Task to label issues based on content."""
        return Task(
            config=self.tasks_config["label_issues"],
            markdown=False,
        )

    @task
    def assign_issues(self) -> Task:
        """Task to assign team members to issues."""
        return Task(
            config=self.tasks_config["assign_issues"],
            markdown=False,
        )

    @task
    def assess_issues(self) -> Task:
        """Task to provide assessment comments on issues."""
        return Task(
            config=self.tasks_config["assess_issues"],
            markdown=True,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the GitHub Issue Management crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

