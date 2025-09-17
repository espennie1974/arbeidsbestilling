document.getElementById("loadTasks").addEventListener("click", async () => {
  const res = await fetch("/tasks");
  const tasks = await res.json();
  const list = document.getElementById("taskList");
  list.innerHTML = "";
  tasks.forEach(task => {
    const li = document.createElement("li");
    li.textContent = `${task.id}: ${task.title} (${task.status})`;
    list.appendChild(li);
  });
});
