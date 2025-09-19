async function fetchTasks() {
  const response = await fetch("/tasks");
  const tasks = await response.json();

  const taskList = document.getElementById("taskList");
  taskList.innerHTML = "";

  tasks.forEach(task => {
    const div = document.createElement("div");
    div.className = "task";
    div.innerHTML = `
      <h3>${task.title}</h3>
      <p>${task.description}</p>
      <p><strong>Opprettet av:</strong> ${task.created_by}</p>
      <p><strong>Tildelt til:</strong> ${task.assigned_to}</p>
      <p><strong>Status:</strong> ${task.status}</p>
      <p><small>Opprettet: ${task.created_at}</small></p>
    `;
    taskList.appendChild(div);
  });
}

document.getElementById("taskForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    created_by: document.getElementById("created_by").value,
    assigned_to: document.getElementById("assigned_to").value
  };

  await fetch("/add_task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  e.target.reset();
  fetchTasks();
});

// Last inn oppdrag når siden åpner
fetchTasks();
