// Når siden lastes inn
document.addEventListener("DOMContentLoaded", () => {
  loadTasks();

  const form = document.getElementById("task-form");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    addTask();
  });
});

// Hent og vis alle oppdrag
function loadTasks() {
  fetch("/tasks")
    .then(res => res.json())
    .then(tasks => {
      const taskList = document.getElementById("task-list");
      taskList.innerHTML = "";
      tasks.forEach(task => {
        const li = document.createElement("li");
        li.innerHTML = `
          <strong>${task.title}</strong> - ${task.description} <br>
          Opprettet av: ${task.created_by}, Tildelt til: ${task.assigned_to} <br>
          Status: <em>${task.status}</em> <br>
          <button onclick="updateStatus(${task.id}, 'Fullført')">✅ Fullfør</button>
          <button onclick="deleteTask(${task.id})">❌ Slett</button>
        `;
        taskList.appendChild(li);
      });
    });
}

// Legg til nytt oppdrag
function addTask() {
  const title = document.getElementById("title").value;
  const description = document.getElementById("description").value;
  const createdBy = document.getElementById("created_by").value;
  const assignedTo = document.getElementById("assigned_to").value;

  fetch("/add_task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title,
      description,
      created_by: createdBy,
      assigned_to: assignedTo
    })
  })
    .then(() => {
      document.getElementById("task-form").reset();
      loadTasks();
    });
}

// Oppdater status på oppdrag
function updateStatus(id, newStatus) {
  fetch(`/update_status/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus })
  }).then(() => loadTasks());
}

// Slett oppdrag
function deleteTask(id) {
  fetch(`/delete_task/${id}`, { method: "DELETE" })
    .then(() => loadTasks());
}
