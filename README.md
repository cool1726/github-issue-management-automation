# GitHub Issue Management Automation

CrewAI를 사용하여 GitHub 이슈를 자동으로 모니터링, 라벨링, 담당자 할당 및 평가하는 멀티 에이전트 시스템입니다.

## 기능

- **이슈 모니터링**: 새로 생성된 GitHub 이슈를 자동으로 감지하고 조회
- **자동 라벨링**: 이슈 내용을 분석하여 적절한 라벨 자동 할당 (bug, feature-request, documentation, question, enhancement 등)
- **담당자 할당**: 팀 멤버의 전문성(frontend, backend, devops, documentation)을 기반으로 적절한 담당자 자동 할당
- **초기 평가**: 버그 리포트의 재현 단계 및 디버깅 제안, 기능 요청의 구현 제안, 문서화 가이드 제공

## 프로젝트 구조

```
github_issue_management/
├── pyproject.toml          # 프로젝트 설정 및 의존성
├── README.md               # 프로젝트 문서
├── src/
│   └── github_issue_management/
│       ├── __init__.py
│       ├── crew.py         # Crew 클래스 정의
│       ├── main.py         # 실행 진입점
│       ├── config/
│       │   ├── agents.yaml # Agent 설정
│       │   └── tasks.yaml  # Task 설정
│       └── tools/
│           ├── __init__.py
│           └── github_tools.py  # GitHub API 툴
```

## 설치

### 1. 의존성 설치

이 프로젝트는 `uv`를 사용하여 패키지를 관리합니다.

```bash
uv sync
```

또는 pip를 사용하는 경우:

```bash
pip install -e .
```

### 2. 환경 변수 설정

GitHub API를 사용하기 위해 GitHub Personal Access Token이 필요합니다.

```bash
export GITHUB_TOKEN="your_github_token_here"
```

GitHub Personal Access Token 생성 방법:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. 필요한 권한 선택:
   - `repo` (전체 저장소 접근)
   - `issues` (이슈 읽기/쓰기)
   - `assignees` (담당자 할당)

## 사용 방법

### 기본 실행

```bash
# 스크립트를 통해 실행
run_crew

# 또는 직접 실행
python -m github_issue_management.main

# 또는 CrewAI CLI 사용
crewai run
```

### 설정 수정

`src/github_issue_management/main.py` 파일에서 다음 설정을 수정하세요:

```python
inputs = {
    "repository": "owner/repo",  # 모니터링할 저장소
    "team_members": {
        "frontend": ["username1", "username2"],
        "backend": ["username3", "username4"],
        "devops": ["username5"],
        "documentation": ["username6"],
    },
}
```

### 기타 명령어

```bash
# 학습
crewai train

# 테스트
crewai test

# 재실행
crewai replay

# 채팅 모드
crewai chat
```

## Agent 설명

### 1. Issue Monitor
- 새 GitHub 이슈를 모니터링하고 조회
- 처리되지 않은 이슈 식별

### 2. Labeler
- 이슈 내용을 분석하여 적절한 라벨 할당
- bug, feature-request, documentation 등으로 분류

### 3. Assigner
- 팀 멤버의 전문성을 기반으로 담당자 할당
- 이슈의 기술적 요구사항과 복잡도 고려

### 4. Assessor
- 초기 평가 댓글 제공
- 버그: 재현 단계 및 잠재적 원인 분석
- 기능 요청: 구현 제안 및 기술적 고려사항
- 문서화: 필요한 문서 구조 및 내용 가이드

## Task 흐름

1. **monitor_issues**: 새 이슈 모니터링 및 조회
2. **label_issues**: 이슈 내용 분석 및 라벨 할당
3. **assign_issues**: 적절한 팀 멤버에게 담당자 할당
4. **assess_issues**: 초기 평가 댓글 작성

## 커스텀 툴

### GetNewIssues
새 GitHub 이슈를 조회합니다.

### AddLabelToIssue
이슈에 라벨을 추가합니다.

### AssignIssue
이슈에 담당자를 할당합니다.

### CommentOnIssue
이슈에 댓글을 추가합니다.

## 주의사항

- GitHub API rate limit을 고려하여 사용하세요
- GITHUB_TOKEN 환경 변수가 설정되어 있어야 합니다
- 저장소에 적절한 라벨이 미리 생성되어 있어야 합니다
- 담당자로 할당할 사용자 이름이 정확해야 합니다

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

