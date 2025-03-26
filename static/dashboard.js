document.addEventListener("DOMContentLoaded", function () {
  const labelsContainer = document.getElementById("labels-container");

  fetch("/fetch-labels")
    .then((response) => response.json())
    .then((labels) => {
      labels.forEach((labelName) => {
        // Create checkbox element
        let fieldDiv = document.createElement("div");
        fieldDiv.classList.add("field");

        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = labelName;
        checkbox.name = "labels";
        checkbox.value = labelName; // Store only the name

        let labelTag = document.createElement("label");
        labelTag.htmlFor = labelName;
        labelTag.textContent = labelName; // Use labelName directly

        fieldDiv.appendChild(checkbox);
        fieldDiv.appendChild(labelTag);
        labelsContainer.appendChild(fieldDiv);
      });
    })
    .catch((error) => {
      console.error("Error fetching labels:", error);
    });
});

function runBot() {
  let button = document.getElementById("run-bot");
  let logDiv = document.getElementById("console-log");

  button.disabled = true;
  appendLog("🔄 Bot is running...");

  // Collect selected labels
  let selectedLabels = [];
  let labelStr = "";
  document
    .querySelectorAll("input[name='labels']:checked")
    .forEach((checkbox) => {
      selectedLabels.push(checkbox.value); // Only send the name
      labelStr += checkbox.id + "   ";
    });

  appendLog("Selected Labels: " + labelStr);
  console.log("Selected Labels:", selectedLabels); // Debugging

  fetch("/run-bot", {
    method: "GET",
  })
    .then((response) => response.text())
    .then((data) => {
      appendLog(data);
      button.disabled = false;
    })
    .catch((error) => {
      appendLog(`❌ Error: ${error}`);
      button.disabled = false;
    });
}

function gmailSetUp() {
  let button = document.getElementById("gmail-set-up");
  appendLog("🔄 Setting up Gmail...");
  button.disabled = true;

  fetch("/gmail-set-up")
    .then((response) => response.text())
    .then((data) => {
      appendLog(data);
    })
    .catch((error) => {
      appendLog(`❌ Error: ${error}`);
    });
}

function appendLog(message) {
  let logDiv = document.getElementById("console-log");
  logDiv.innerHTML += `<p>${message}</p>`;
  logDiv.scrollTop = logDiv.scrollHeight; // Auto-scroll to bottom
}
