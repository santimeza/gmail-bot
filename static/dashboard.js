document.addEventListener("DOMContentLoaded", function () {
  const labelsContainer = document.getElementById("labels-container");

  fetch("/fetch-labels")
    .then((response) => response.json())
    .then((labels) => {
      labels.forEach((labelName) => {
        // Create a field div for each checkbox
        let fieldDiv = document.createElement("div");
        fieldDiv.classList.add("field");

        // Create a control div for styling
        let controlDiv = document.createElement("div");
        controlDiv.classList.add("control");

        // Create the checkbox input
        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = labelName;
        checkbox.name = "labels";
        checkbox.value = labelName; // Store only the name
        checkbox.classList.add("checkbox"); // Add Bulma's checkbox class

        // Create the label for the checkbox
        let labelTag = document.createElement("label");
        labelTag.htmlFor = labelName;
        labelTag.textContent = labelName; // Use labelName directly
        labelTag.style.marginLeft = "0.5rem"; // Add spacing between checkbox and label

        // Append the checkbox and label to the control div
        controlDiv.appendChild(checkbox);
        controlDiv.appendChild(labelTag);

        // Append the control div to the field div
        fieldDiv.appendChild(controlDiv);

        // Append the field div to the labels container
        labelsContainer.appendChild(fieldDiv);
      });
    })
    .catch((error) => {
      console.error("Error fetching labels:", error);
    });
});

// Function runs the gmail cleaner with the given parameters
function runBot() {
  let button = document.getElementById("run-bot");
  let logDiv = document.getElementById("console-log");

  button.disabled = true;

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
  appendLog("🔄 Bot is running...");

  console.log("Selected Labels:", selectedLabels); // Debugging

  fetch("/run-bot", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ labels: selectedLabels }),
  })
    .then((response) => response.json()) // Convert response to JSON
    .then((data) => {
      if (data.message) {
        appendLog(data.message); // Extract and display the message
      } else if (data.error) {
        appendLog(`❌ Error: ${data.error}`); // Handle errors
      }
      button.disabled = false;
    })
    .catch((error) => {
      appendLog(`❌ Fetch error: ${error}`);
      button.disabled = false;
    });
}

// Function to handle the Gmail setup button click, creates the important address label in users gmail account
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

// Function to append log messages to the console log div
function appendLog(message) {
  let logDiv = document.getElementById("console-log");
  logDiv.innerHTML += `<p>${message}</p>`;
  logDiv.scrollTop = logDiv.scrollHeight; // Auto-scroll to bottom
}

// Front end functions to update the date input and days old input
function updateDateFromDays() {
  const daysOldInput = document.getElementById("days-old");
  const beforeDateInput = document.getElementById("before-date");
  const noDateCheckbox = document.getElementById("no-date-restriction");

  if (noDateCheckbox.checked) return; // Do nothing if "No Date Restriction" is checked

  const daysOld = parseInt(daysOldInput.value, 10);
  if (!isNaN(daysOld)) {
    const today = new Date();
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() - daysOld);

    // Format the date as YYYY-MM-DD for the date input
    const formattedDate = targetDate.toISOString().split("T")[0];
    beforeDateInput.value = formattedDate;
  }
}

function updateDaysFromDate() {
  const daysOldInput = document.getElementById("days-old");
  const beforeDateInput = document.getElementById("before-date");
  const noDateCheckbox = document.getElementById("no-date-restriction");

  if (noDateCheckbox.checked) return; // Do nothing if "No Date Restriction" is checked

  const selectedDate = new Date(beforeDateInput.value);
  if (!isNaN(selectedDate)) {
    const today = new Date();
    const diffTime = today - selectedDate;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    daysOldInput.value = diffDays >= 0 ? diffDays : 0; // Ensure no negative days
  }
}

// Function to toggle the date restriction inputs based on the checkbox state
function toggleDateRestriction() {
  const daysOldInput = document.getElementById("days-old");
  const beforeDateInput = document.getElementById("before-date");
  const noDateCheckbox = document.getElementById("no-date-restriction");

  if (noDateCheckbox.checked) {
    // Disable inputs and set default values
    daysOldInput.value = 0;
    daysOldInput.readOnly = true;

    const today = new Date();
    const formattedDate = today.toISOString().split("T")[0];
    beforeDateInput.value = formattedDate;
    beforeDateInput.readOnly = true;
  } else {
    // Enable inputs
    daysOldInput.readOnly = false;
    beforeDateInput.readOnly = false;
  }
}
