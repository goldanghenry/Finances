# GitHub Pages 최초 배포

## 1. GitHub 저장소

1. GitHub에서 **public** 저장소 `Finances` 생성 (이름은 자유, URL에 반영됨).
2. 로컬에서:

```bash
cd /Users/henry/Finances
git add .
git commit -m "Add MkDocs site and GitHub Pages workflow"
git branch -M main
git remote add origin https://github.com/goldanghenry/Finances.git
git push -u origin main
```

## 2. Pages 설정

1. 저장소 **Settings → Pages**
2. **Build and deployment** → Source: **GitHub Actions**
3. `main`에 push되면 [pages.yml](../.github/workflows/pages.yml)이 자동 실행됩니다.

## 3. URL

`https://goldanghenry.github.io/Finances/`

## 4. 로컬 미리보기

```bash
source .venv/bin/activate   # 최초: python3 -m venv .venv && pip install -r requirements-docs.txt
mkdocs serve
```

## 5. 비공개 노트

`private/`는 커밋되지 않습니다. [private-notes.md](private-notes.md) 참고.
