# GitHub Pages 최초 배포

## 1. GitHub 저장소

[goldanghenry/Finances](https://github.com/goldanghenry/Finances)

`main`에 push되면 [pages.yml](../.github/workflows/pages.yml)이 MkDocs를 빌드해 **`gh-pages` 브랜치**에 올립니다.

## 2. Pages 설정 (필수, 1회)

1. [Settings → Pages](https://github.com/goldanghenry/Finances/settings/pages)
2. **Build and deployment**
   - Source: **Deploy from a branch**
   - Branch: **`gh-pages`** · 폴더: **`/ (root)`**
3. 저장 후 1~2분 뒤 접속

> **참고:** Source를 **GitHub Actions**만 켜 두면 `deploy-pages`가 **404**로 실패할 수 있습니다. 이 저장소는 **`gh-pages` 브랜치** 방식을 씁니다.

## 3. URL

[https://goldanghenry.github.io/Finances/](https://goldanghenry.github.io/Finances/)

## 4. 로컬 미리보기

```bash
source .venv/bin/activate   # 최초: python3 -m venv .venv && pip install -r requirements-docs.txt
mkdocs serve
```

## 5. 비공개 노트

`private/`는 커밋되지 않습니다. [private-notes.md](private-notes.md) 참고.
