const input = document.getElementById("text");
const modal = document.getElementById("modal");

const path = window.location.pathname;
const segments = path.split("/").filter(Boolean);
const project_name = segments[1];

document.addEventListener("selectionchange", () => {
    const activeElement = document.activeElement;

    if (activeElement === input) {
        const selectionStart = input.selectionStart;
        const selectionEnd = input.selectionEnd;

        if (selectionStart !== selectionEnd) {
        modal.style.display = "block";
        return;
        }
    }

  modal.style.display = "none";
});

async function extract_entity(ev) {
    const entity = ev.target.id;

    const input = document.getElementById("text");
    const start = input.selectionStart;
    const end = input.selectionEnd;

    const selectedText = input.value.substring(start, end);

    const entities_list = document.getElementById("entities-list");

    const entity_line = document.createElement("div");
    entity_line.classList.add("entity-line");
    entity_line.dataset.start = start;
    entity_line.dataset.end = end;
    
    const entity_name = document.createElement("span");
    entity_name.textContent = selectedText;
    entity_line.appendChild(entity_name);
    const entity_role = document.createElement("span");
    entity_role.textContent = entity;
    entity_line.appendChild(entity_role);
    const value = document.createElement("input");
    value.type = "text";
    value.value = selectedText.trim();
    entity_line.appendChild(value);

    entities_list.appendChild(entity_line);

    document.getElementById("modal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", async () => {
    const project_data = await fetchData();
    const intent_select = document.getElementById("classification");
    const modal = document.getElementById("modal");

    intent_select.innerHTML = '';

    for (const intent of project_data["intents"]){
        const option = document.createElement("option");
        option.value = intent;
        option.textContent = intent;
        intent_select.appendChild(option);
    }

    for (const entity of project_data["entities"]){
        const option = document.createElement("button");
        const br = document.createElement("br");
        option.textContent = entity;
        option.onclick = extract_entity
        option.id = entity
        modal.appendChild(option);
        modal.appendChild(br);
    }
});

async function fetchData() {
    try {
        const response = await fetch(`/project-info/${project_name}`);

        if (!response.ok) {
        throw new Error("Request error: " + response.status);
        }
        return await response.json();

    } catch (error) {
        console.error("Error", error);
    }
}

async function submit() {
    const text_input = document.getElementById("text");
    const intent_select = document.getElementById("classification");
    const entity_list = document.getElementsByClassName("entity-line")

    form = {
        "text": text_input.value,
        "classification": intent_select.value,
        "slots": []
    }
    text_input.value = "";

    for (const entity_line of entity_list){
        const slot = {
            "start": entity_line.dataset.start,
            "end": entity_line.dataset.end,
            "entity": entity_line.childNodes[1].textContent,
            "value": entity_line.childNodes[2].value
        }
        form.slots.push(slot)
    }
    document.querySelectorAll(".entity-line").forEach(el => el.remove());
    
    fetch(`/api/update-dataset/${project_name}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
    })

}
