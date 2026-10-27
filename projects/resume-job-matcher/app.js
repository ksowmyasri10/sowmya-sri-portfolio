"use strict";

const form = document.querySelector("#match-form");
const resumeInput = document.querySelector("#resume-text");
const jobInput = document.querySelector("#job-text");
const submitButton = document.querySelector("#match-button");
const errorOutput = document.querySelector("#form-error");
const results = document.querySelector("#results");
const MAX_FILE_BYTES = 5 * 1024 * 1024;
const MAX_TEXT_CHARS = 60000;

const examples = {
  resume: `PROJECT EXPERIENCE
Credit Card Default Prediction
Python, scikit-learn, pandas, NumPy, matplotlib, seaborn. Applied data preprocessing, feature engineering, and exploratory data analysis. Compared Logistic Regression, Random Forest, and SVM models; reported accuracy: 85%.

EEG Emotion Recognition for Parkinson's Research
Python, TensorFlow, Keras, pandas, NumPy, scikit-learn. Explored deep-learning emotion classification from EEG signals and Delta, Theta, Alpha, and Beta frequency bands.

SKILLS
Python, Java, C++, SQL, Machine Learning, Classification, Model Evaluation, Feature Engineering.`,
  job: `Machine Learning Engineer
Required skills: Python, machine learning, scikit-learn, pandas, NumPy, feature engineering, classification, model evaluation, SQL, TensorFlow, NLP, and Docker.
Responsibilities include building and evaluating predictive models, preparing datasets, and communicating results with a cross-functional team.`
};

function updateCounter(textarea, counterId) {
  document.querySelector(`#${counterId}`).textContent =
    `${textarea.value.length.toLocaleString()} / ${MAX_TEXT_CHARS.toLocaleString()}`;
}

resumeInput.addEventListener("input", () => updateCounter(resumeInput, "resume-count"));
jobInput.addEventListener("input", () => updateCounter(jobInput, "job-count"));

function bufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunkSize = 0x8000;
  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + chunkSize));
  }
  return btoa(binary);
}

async function loadFile(input, textarea, statusId) {
  const file = input.files?.[0];
  if (!file) return;
  const status = document.querySelector(`#${statusId}`);
  if (file.size > MAX_FILE_BYTES) {
    status.textContent = "File must be smaller than 5 MB.";
    input.value = "";
    return;
  }
  status.textContent = `Reading ${file.name} locally…`;
  try {
    const response = await fetch("/api/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: file.name, content_base64: bufferToBase64(await file.arrayBuffer()) })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not read this file.");
    textarea.value = result.text;
    textarea.dispatchEvent(new Event("input"));
    status.textContent = `Loaded ${file.name} locally.`;
  } catch (error) {
    status.textContent = error.message || "Could not read this file.";
  } finally {
    input.value = "";
  }
}

document.querySelector("#resume-file").addEventListener("change", event => {
  loadFile(event.currentTarget, resumeInput, "resume-status");
});
document.querySelector("#job-file").addEventListener("change", event => {
  loadFile(event.currentTarget, jobInput, "job-status");
});

document.querySelector("#sample-button").addEventListener("click", () => {
  resumeInput.value = examples.resume;
  jobInput.value = examples.job;
  resumeInput.dispatchEvent(new Event("input"));
  jobInput.dispatchEvent(new Event("input"));
  document.querySelector("#resume-status").textContent = "Sample text loaded. Replace it with your own.";
  document.querySelector("#job-status").textContent = "Sample text loaded. Replace it with your own.";
  errorOutput.textContent = "";
});

function renderSkills(elementId, skills, emptyMessage) {
  const container = document.querySelector(`#${elementId}`);
  container.replaceChildren();
  if (!skills.length) {
    const empty = document.createElement("span");
    empty.className = "empty-result";
    empty.textContent = emptyMessage;
    container.append(empty);
    return;
  }
  for (const skill of skills) {
    const chip = document.createElement("span");
    chip.className = "skill-chip";
    chip.textContent = skill.name;
    chip.title = skill.category;
    container.append(chip);
  }
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  errorOutput.textContent = "";
  if (!resumeInput.value.trim() || !jobInput.value.trim()) {
    errorOutput.textContent = "Paste or upload both your resume and the job description.";
    return;
  }
  submitButton.disabled = true;
  submitButton.innerHTML = "Comparing locally…";
  try {
    const response = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeInput.value, job_text: jobInput.value })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not compare these documents.");

    document.querySelector("#score-number").textContent =
      result.score === null ? "—" : `${result.score}%`;
    document.querySelector("#score-label").textContent = result.score_label;
    document.querySelector("#score-title").textContent =
      result.score === null ? "No recognized job skills" : "Recognized skill coverage";
    const progress = document.querySelector("#score-progress");
    progress.setAttribute("aria-valuenow", result.score ?? 0);
    progress.setAttribute("aria-valuetext", result.score_label);
    document.querySelector("#score-fill").style.width = `${result.score ?? 0}%`;
    renderSkills("matched-list", result.matched, "No recognized skill overlap yet.");
    renderSkills("missing-list", result.missing, "No recognized job skills are missing.");
    renderSkills("additional-list", result.additional, "No additional catalogued skills found.");
    document.querySelector("#disclaimer").textContent = result.disclaimer;
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    errorOutput.textContent = error.message || "The local matcher is unavailable. Restart the Python app and try again.";
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = 'Compare skills <span aria-hidden="true">→</span>';
  }
});

document.querySelector("#clear-button").addEventListener("click", () => {
  resumeInput.value = "";
  jobInput.value = "";
  resumeInput.dispatchEvent(new Event("input"));
  jobInput.dispatchEvent(new Event("input"));
  document.querySelector("#resume-status").textContent = "Your resume stays on this device.";
  document.querySelector("#job-status").textContent = "Only used for this comparison.";
  errorOutput.textContent = "";
  results.hidden = true;
  document.querySelector("#resume-status").textContent = "Text cleared.";
  document.querySelector("#job-status").textContent = "Text cleared.";
  resumeInput.focus();
});
