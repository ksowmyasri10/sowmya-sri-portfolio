# Kambhampati Sowmya Sri — Portfolio

## Live portfolio

The public website is deployed at [https://ksowmyasri10.github.io/sowmya-sri-portfolio/](https://ksowmyasri10.github.io/sowmya-sri-portfolio/). The chatbot uses its portfolio-grounded local answers on GitHub Pages; the optional AI API integration is available when running the Node server.

## Run in VS Code

1. Install [Node.js 18 or newer](https://nodejs.org/).
2. Open the extracted project folder in VS Code.
3. Open the integrated terminal and run:

```sh
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

No package installation is required. Without an API key, the assistant answers common questions from the portfolio locally and says when a detail is not listed.

## Enable AI answers

Copy `.env.example` to `.env`, add your OpenAI API key to `OPENAI_API_KEY`, then restart the server. You can optionally change `OPENAI_MODEL` or `PORT`. The key is read by the server only and is never sent to the browser. Do not commit `.env`.

The portfolio and chatbot are based on the provided resume details. The Parkinson's EEG project is linked to its GitHub repository and is described as educational research, not a clinical diagnostic tool.

## RoleMatch — Private Resume Matcher

RoleMatch is published as a separate repository: [RoleMatch-Private-Resume-Matcher](https://github.com/ksowmyasri10/RoleMatch-Private-Resume-Matcher). Its local source folder is `projects/resume-job-matcher/`. The Python app compares recognized skills in a resume and job description, supports TXT, MD, PDF, and DOCX, reports a transparent keyword-coverage estimate, and does not send documents to an external service or save them. The estimate is not an ATS score or hiring prediction.

The ATS resume PDF is available from the portfolio's **Download resume (PDF)** link.

## GitHub Pages deployment

The included GitHub Actions workflow deploys the static portfolio to GitHub Pages whenever changes are pushed to `main`. Enable GitHub Pages in the repository settings and select **GitHub Actions** as the build and deployment source if it is not already enabled. Do not upload `.env` or your API key. The `.gitignore` excludes `.env` and `node_modules`.

GitHub Pages does not run the Node server; the chatbot therefore uses local answers on the published site. To enable AI answers online, deploy the Node backend separately and configure its API key as a server-side secret.
