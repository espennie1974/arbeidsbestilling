async function fetchTasks() {
    const res = await fetch("/tasks");
    const tasks = await res.json();

    const taskList = document.getElementById("taskList");
    taskList.innerHTML = "";
    tasks.forEach(task => {
        const li = document.createElement("li");
        li.textContent = `${task.title} - ${task.description} (Status: ${task.status})`;
        taskList.appendChild(li);
    });
}

document.getElementById("taskForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const task = {
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        created_by: document.getElementById("created_by").value,
        assigned_to: document.getElementById("assigned_to").value,
    };

    await fetch("/add_task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(task)
    });

    document.getElementById("taskForm").reset();
    fetchTasks();
});

fetchTasks();

