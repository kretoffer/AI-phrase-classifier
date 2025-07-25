import { extract_entity, delete_slot } from "./extract_entity.js";

const path = window.location.pathname;
const segments = path.split("/").filter(Boolean);
const project_name = segments[0];
const element_id = segments[2];

async function fetchProjectData() {
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

async function fetchElementData() {
    try {
        const response = await fetch(`/api/dataset-hand-element-data/${project_name}/${element_id}`);

        if (!response.ok) {
        throw new Error("Request error: " + response.status);
        }
        return await response.json();

    } catch (error) {
        console.error("Error", error);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const project_data = await fetchProjectData();
    const element_data = await fetchElementData();
    const intent_select = document.getElementById("classification");
    const modal = document.getElementById("modal");
    const phrase_input = document.getElementById("text")

    intent_select.innerHTML = '';

    for (const intent of project_data["intents"]){
        const option = document.createElement("option");
        option.value = intent;
        option.textContent = intent;
        intent_select.appendChild(option);
    }

    intent_select.value=element_data.classification
    phrase_input.value = element_data.text

    load_slots(element_data.slots)

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

function load_slots(slots) {
    for (const slot of slots){
        load_slot(slot)
    }
}

function load_slot(slot) {
    const phrase_input = document.getElementById("text")
    const entities_list = document.getElementById("entities-list");

    const entity_line = document.createElement("div");
    entity_line.classList.add("entity-line");
    entity_line.dataset.start = slot.start;
    entity_line.dataset.end = slot.end;

    const selectedText = phrase_input.value.substring(slot.start, slot.end)
    
    const entity_name = document.createElement("span");
    entity_name.textContent = selectedText;
    entity_line.appendChild(entity_name);
    const entity_role = document.createElement("span");
    entity_role.textContent = slot.entity;
    entity_line.appendChild(entity_role);
    const value = document.createElement("input");
    value.type = "text";
    value.value = slot.value;
    entity_line.appendChild(value);
    const delete_button = document.createElement("button");
    delete_button.textContent = "X";
    delete_button.onclick = delete_slot;
    delete_button.classList.add("entity-delete");
    entity_line.appendChild(delete_button);

    entities_list.appendChild(entity_line);
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

    for (const entity_line of entity_list){
        const slot = {
            "start": entity_line.dataset.start,
            "end": entity_line.dataset.end,
            "entity": entity_line.childNodes[1].textContent,
            "value": entity_line.childNodes[2].value
        }
        form.slots.push(slot)
    }
    
    fetch(`/api/update-hand-element/${project_name}/${element_id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
    })
    window.location.href = `/web/project/${project_name}/edit/dataset/view`
}

function delete_element(){
    fetch(`/api/delete-hand-element/${project_name}/${element_id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok){
            console.error(`Error: ${response.status}`);
        }
    });
    window.location.href = `/web/project/${project_name}/edit/dataset/view`
}

window.submit = submit;
window.delete_element = delete_element;
