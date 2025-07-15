<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Patient Management Dashboard</title>
  <link rel="stylesheet" href="/static/style.css"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet"/>
</head>
<body>
  <header>
    <h1>👨‍⚕️ Patient Management System</h1>
    <div style="text-align: right;">
      <a href="/logout" style="color: white; font-weight: bold; text-decoration: underline;">🔓 Logout</a>
    </div>
  </header>

  <main class="dashboard">
    <section class="card">
      <h2>➕ Add New Patient</h2>
      <form id="patientForm">
        <div class="form-row">
          <input required type="text" name="P_name" placeholder="Full Name">
          <input required type="number" name="age" placeholder="Age">
        </div>
        <div class="form-row">
          <input required type="text" name="Disease" placeholder="Disease">
          <input required type="text" name="Doc_Incharge" placeholder="Doctor In-Charge">
          <input required type="number" name="fee" placeholder="Fee (₹)">
        </div>
        <button type="submit">Add Patient</button>
      </form>
    </section>

    <section class="card">
      <h2>📋 All Patients</h2>
      <input type="text" id="searchBox" placeholder="Search by name or disease..." />
      <table id="patientTable">
        <thead>
          <tr>
            <th>ID</th><th>Name</th><th>Age</th><th>Disease</th>
            <th>Doctor</th><th>Fee (₹)</th><th>Actions</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </section>
  </main>

  <footer><p>🧠 Built by Ashmeet | Flask + MySQL + JS</p></footer>

  <div id="toast"></div>

  <script src="/static/script.js"></script>
</body>
</html>
