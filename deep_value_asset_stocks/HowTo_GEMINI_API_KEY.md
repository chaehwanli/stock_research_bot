Gemini API Key (Google AI Studio) 발급 방법은 다음과 같습니다.

1. Google AI Studio 접속
- https://aistudio.google.com/ 에 접속합니다.
- 구글 계정으로 로그인합니다.

2. API Key 받기
- 좌측 상단(또는 메인 화면)의 "Get API key" 버튼을 클릭합니다.
- **"Create API key"**를 누릅니다.
- "Create API key in new project" (또는 기존 프로젝트 선택)를 클릭합니다.

3. 키 복사 및 적용
- 생성된 AIza로 시작하는 긴 문자열을 복사합니다.
- .env 파일의 OPENAI_API_KEY 부분을 GEMINI_API_KEY로 변경하고 붙여넣으시면 됩니다. (또는 코드에서 지원하는 이름으로 설정)

## 참고: 작성해주신 
requirements.txt
에 google-generativeai가 포함되어 있으므로, 봇 코드에서는 이 키를 사용하여 Gemini 모델을 호출하게 됩니다.