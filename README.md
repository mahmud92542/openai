# Deploy Assistant to OpenAI

This repository contains a GitHub Actions workflow designed to automate the deployment of assistant configurations to the OpenAI platform. The workflow ensures your assistant remains updated through a controlled CI/CD pipeline. Changes go through automated testing and manual approval before reaching production. This helps ensure the assistant remains functional, accurate, and reliable.

---

## Workflow Overview

The GitHub Actions workflow, defined in `.github/workflows/prod_deployment.yml`, consists of two main jobs: **CI** and **CD**. This structured approach ensures a reliable assistant deployment process.

### CI: Continuous Integration

* Triggered automatically when a pull request is created targeting the `main` branch.
* Creates a **temporary assistant** using the updated configuration.
* Runs unit and integration tests using `pytest` to validate functionality.
* Deletes the temporary assistant after testing — **even if the tests fail**.
* If tests fail, the workflow stops and deployment to production is not allowed.

### CD: Continuous Deployment

* If the CI job passes, the workflow pauses for **manual approval**.
* Deployment to the production environment occurs only after approval via the GitHub UI.
* There is **only one environment**, called `production`, which contains a variable named `PROD_ASSISTANT_ID`.

---

## Configuration File

The assistant configuration is stored in `assistant_config.json`. This file must be a valid JSON document and should contain the following fields:

```json
{
  "instructions": "Provide user-friendly and accurate responses.",
  "tools": ["search", "translator"],
  "model": "gpt-4-turbo"
}
```

---

## Secrets

To enable this workflow, you must configure the following secrets in your GitHub repository:

* `OPENAI_API_KEY`: API key with permissions to manage OpenAI assistants.
* `PROD_ASSISTANT_ID`: The assistant ID used in the production environment.

> ⚠️ **Note:** There is no separate development environment. A temporary assistant is created dynamically during CI testing.

### Setting Up Secrets

1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Add each secret as a new entry.

---

## Debugging and Logs

### Debugging the Payload

The payload sent to the OpenAI API is logged during execution to help identify formatting or content issues.

### Logs Include:

* Extracted assistant ID.
* Test results and pass percentage.
* API request and response information.
* Assistant creation and deletion status.

---

## Common Issues and Resolutions

1. **Configuration File Not Found**
   Ensure `assistant_config.json` exists at the repository root.

2. **Invalid JSON Format**
   Use tools like `jq` or online JSON validators to check syntax.

3. **Test Failures**
   Fix failing tests in the codebase before continuing with the deployment.

4. **API Request Fails**
   Double-check that your secrets are correct and your payload adheres to OpenAI's API specifications.

---

## How to Use

1. **Create a Branch**
   Create a new branch from `main` for your changes. Direct pushes to `main` are not allowed.

2. **Implement and Commit Changes**
   Update `assistant_config.json` or related code and push to your new branch.

3. **Open a Pull Request**
   Submit a pull request from your branch to `main`. This triggers the CI process.

4. **Pass CI Tests**
   A temporary assistant is created, tests are run, and the assistant is deleted afterward. Fix any issues if the tests fail.

5. **Request Production Approval**
   Once CI is successful, a manager or repository admin must approve the production deployment in **Environments > production**.

6. **Monitor Workflow**
   Use the **Actions** tab in GitHub to monitor the status and review logs.

---

This CI/CD pipeline guarantees a robust, secure, and controlled way to manage assistant configurations on the OpenAI platform.
