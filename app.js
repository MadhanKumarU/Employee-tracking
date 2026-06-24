// Format seconds into h m s
function formatHMS(sec) {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  return `${h}h ${m}m ${s}s`;
}

async function loadEmployees() {
  const res = await fetch("/employees");
  const data = await res.json();

  const sel = document.getElementById("employeeSelect");
  sel.innerHTML = "";

  data.forEach(emp => {
    const opt = document.createElement("option");
    opt.value = emp.employee_code;
    opt.textContent = `${emp.employee_code} (${emp.system_name || "N/A"})`;
    sel.appendChild(opt);
  });

  // Set today's date by default
  document.getElementById("datePicker").value =
    new Date().toISOString().slice(0, 10);
}

async function loadUsage() {
  const emp = document.getElementById("employeeSelect").value;
  const date = document.getElementById("datePicker").value;

  const res = await fetch(`/usage/${emp}?date_str=${date}`);
  const data = await res.json();

  const list = document.getElementById("usageContainer");
  list.innerHTML = "";

  if (!data.apps || data.apps.length === 0) {
    list.innerHTML = `<div class="item">No data for ${date}</div>`;
    return;
  }

  data.apps.sort((a,b) => b.total_seconds - a.total_seconds);

  data.apps.forEach(a => {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML =
      `<div class="name">${a.app}</div>
       <div class="sec">${formatHMS(a.total_seconds)}</div>`;
    list.appendChild(div);
  });
}

async function loadLive() {
  const res = await fetch("/live");
  const data = await res.json();

  const list = document.getElementById("liveContainer");
  list.innerHTML = "";

  for (let emp in data) {
    const title = document.createElement("div");
    title.style.fontWeight = "700";
    title.style.margin = "10px 0 6px";
    title.textContent = emp;
    list.appendChild(title);

    data[emp].forEach(a => {
      const div = document.createElement("div");
      div.className = "item";
      div.innerHTML =
        `<div class="name">${a.app}</div>
         <div class="sec">${formatHMS(a.total_seconds)}</div>`;
      list.appendChild(div);
    });
  }
}

document.getElementById("loadBtn").addEventListener("click", loadUsage);

// Live refresh every 5s
setInterval(loadLive, 5000);

// Init
(async function init(){
  await loadEmployees();
  await loadUsage();
  await loadLive();
})();
