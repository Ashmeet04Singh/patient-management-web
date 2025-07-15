window.onload = () => {
  loadPatients();
  document.getElementById("patientForm").addEventListener("submit", addPatient);
  document.getElementById("searchBox").addEventListener("input", filterPatients);
};

let allPatients = [];

function addPatient(e) {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());

  if (!data.P_name || !data.age || !data.Disease || !data.Doc_Incharge || !data.fee) {
    return toast("❗ Please fill all fields", "error");
  }

  data.age = +data.age;
  data.fee = +data.fee;

  fetch("/patients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(res => {
      toast(res.message || "Patient added!");
      loadPatients();       // ✅ Refresh list after adding
      e.target.reset();     // ✅ Clear the form
    })
    .catch(err => toast("❌ Error adding patient", "error"));
}

function loadPatients() {
  fetch("/patients")
    .then(res => res.json())
    .then(data => {
      allPatients = data;
      renderPatients(data);
    });
}

function renderPatients(data) {
  const tbody = document.querySelector("#patientTable tbody");
  tbody.innerHTML = "";

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7">No patients found.</td></tr>`;
    return;
  }

  data.forEach(p => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${p.P_id}</td>
      <td>${p.P_name}</td>
      <td>${p.age}</td>
      <td>${p.Disease}</td>
      <td>${p.Doc_Incharge}</td>
      <td>₹${p.fee}</td>
      <td>
        <button class="update-btn" onclick="promptUpdate(${p.P_id}, ${p.fee})">Update Fee</button>
        <button class="delete-btn" onclick="deletePatient(${p.P_id})">Delete</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

function deletePatient(id) {
  if (!confirm(`Delete patient ID ${id}?`)) return;
  fetch(`/patients/${id}`, { method: "DELETE" })
    .then(res => res.json())
    .then(res => {
      toast(res.message || "Deleted");
      loadPatients();
    })
    .catch(() => toast("❌ Error deleting", "error"));
}

function promptUpdate(id, currentFee) {
  const fee = prompt(`Current fee: ₹${currentFee}\nEnter new fee:`);
  if (fee === null) return;
  const newFee = parseInt(fee);
  if (isNaN(newFee) || newFee < 0) return toast("Invalid fee entered", "error");

  fetch(`/patients/${id}/fee`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fee: newFee })
  })
    .then(res => res.json())
    .then(res => {
      toast(res.message || "Fee updated");
      loadPatients();
    })
    .catch(() => toast("❌ Error updating fee", "error"));
}

function filterPatients() {
  const search = document.getElementById("searchBox").value.toLowerCase();
  const filtered = allPatients.filter(p =>
    p.P_name.toLowerCase().includes(search) ||
    p.Disease.toLowerCase().includes(search)
  );
  renderPatients(filtered);
}

function toast(msg, type = "") {
  const toastEl = document.getElementById("toast");
  toastEl.className = `show ${type}`;
  toastEl.innerText = msg;
  setTimeout(() => { toastEl.className = toastEl.className.replace("show", ""); }, 3000);
}
