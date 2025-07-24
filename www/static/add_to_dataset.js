import { extract_entity } from './extract_entity.js'

const path = window.location.pathname;
const segments = path.split("/").filter(Boolean);
const project_name = segments[1];

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
        const response = await fetch(`/api/project-info/${project_name}`);

        if (!response.ok) {
        throw new Error("Request error: " + response.status);
        }
        return await response.json();

    } catch (error) {
        console.error("Error", error);
    }
}

function submit() {
    const text_input = document.getElementById("text");
    const intent_select = document.getElementById("classification");
    const entity_list = document.getElementsByClassName("entity-line")

    let form = {
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
window.submit = submit;
