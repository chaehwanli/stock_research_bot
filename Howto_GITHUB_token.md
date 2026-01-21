GitHub Token(Personal Access Token)은 GitHub 웹사이트에서 직접 생성해야 합니다. 기존 비밀번호 대신 사용하는 보안 인증 수단입니다.

다음 단계에 따라 생성하고 .env 파일에 추가해 주세요.

## 1단계: 토큰 생성하기

1. **GitHub 설정 페이지**로 이동합니다.
- 경로: GitHub 우측 상단 프로필 클릭 -> Settings -> 왼쪽 메뉴 맨 아래 Developer settings -> Personal access tokens -> Tokens (classic)
2. Generate new token 클릭 -> Generate new token (classic) 선택.
3. Note: 토큰 이름 입력 (예: StockBot)
4. Expiration: 만료 기한 설정 (로컬 봇용이라면 No expiration 또는 원하시는 기간 설정)
5. Select scopes (중요):
- repo 박스를 체크하세요. (이 권한이 있어야 Wiki에 글을 쓸 수 있습니다.)
6. 맨 아래 Generate token 클릭.
7. 나타나는 ghp_... 로 시작하는 긴 문자열을 복사하세요. (화면을 나가면 다시 볼 수 없습니다!)

## 2단계: 프로젝트에 적용하기
지금 열려 있는 .env 파일에 아래 줄을 추가하고 저장하세요 (3번째 줄이나 빈 곳에).

```bash
GITHUB_TOKEN="복사한_토큰_붙여넣기"
```

저장 후 봇을 다시 실행하면 인증 오류 없이 Wiki에 리포트가 게시될 것입니다.