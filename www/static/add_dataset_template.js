const path = window.location.pathname;
const segments = path.split("/").filter(Boolean);
const project_name = segments[1];

function delete_slot(ev){
    const line = ev.target.parentElement;
    line.remove();
}

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

function add_entity(ev){
    const role = ev.target.dataset.entity;
    const input = document.getElementById(`${role}_input`)
    const entity_list = document.getElementById(`${role}_list`)

    const line = document.createElement("div");
    line.classList.add("template-entity-line", `${role}-line`);
    const text = document.createElement("input");
    text.value = input.value;
    line.appendChild(text);
    const value = document.createElement("input");
    value.value = input.value;
    line.appendChild(value);
    const delete_button = document.createElement("button");
    delete_button.textContent = "X";
    delete_button.onclick = delete_slot;
    delete_button.classList.add("entity-delete");
    line.appendChild(delete_button);

    entity_list.appendChild(line);

    input.value = "";
}

document.addEventListener("DOMContentLoaded", async () => {
    const project_data = await fetchProjectData();
    const intent_select = document.getElementById("classification");
    const entities_container = document.getElementById("entities-container");

    intent_select.innerHTML = '';

    for (const intent of project_data["intents"]){
        const option = document.createElement("option");
        option.value = intent;
        option.textContent = intent;
        intent_select.appendChild(option);
    }

    for (const entity of project_data["entities"]){
        const entity_list = document.createElement("div");
        entity_list.id = `${entity}_list`;
        entity_list.classList.add("contant-div");
        const label = document.createElement("h5");
        label.textContent = entity;
        entity_list.appendChild(label);
        const add_entity_input = document.createElement("input");
        add_entity_input.type = "text";
        add_entity_input.id = `${entity}_input`;
        add_entity_input.style = "width: 90%; display: inline-block; margin-right: 1%;";
        entity_list.appendChild(add_entity_input);
        const add_entity_button = document.createElement("button");
        add_entity_button.classList.add("btn", "btn-primary");
        add_entity_button.dataset.entity = entity;
        add_entity_button.textContent = "Add +"
        add_entity_button.style = "display: inline-block; font-weight: 700; width: 9%;";
        add_entity_button.onclick = add_entity;
        entity_list.appendChild(add_entity_button);

        const labels = document.createElement("div");
        labels.classList.add("entity-labels");
        const entity_text = document.createElement("span");
        entity_text.textContent = "text";
        labels.appendChild(entity_text);
        const entity_value = document.createElement("span");
        entity_value.textContent = "value";
        labels.appendChild(entity_value);
        const delete_button = document.createElement("span");
        delete_button.textContent = "delete";
        delete_button.classList.add("entity-delete");
        labels.appendChild(delete_button);
        entity_list.appendChild(labels);
        const separotor = document.createElement("div");
        separotor.style = "width: 100%; background: #c5c5c5; height: 1px; margin: 2px 0 12px 0;";
        entity_list.appendChild(separotor);


        entities_container.appendChild(entity_list);
    }
});

function add_phrase(){
    const phrases_div = document.getElementById("phrases-div");
    const phrase_input = document.getElementById("phrases-input");
    const phrase_line = document.createElement("div");
    const phrase = document.createElement("input");
    phrase.type = "text";
    phrase.value = phrase_input.value;
    phrase_line.classList.add("phrase-line");
    phrase_line.appendChild(phrase);
    const delete_button = document.createElement("button");
    delete_button.textContent = "X";
    delete_button.onclick = delete_slot;
    delete_button.classList.add("entity-delete");
    phrase_line.appendChild(delete_button);

    phrases_div.appendChild(phrase_line);

    phrase_input.value = "";
}

async function submit(){
    const project_data = await fetchProjectData();
    const intent = document.getElementById("classification").value;
    const phrase_lines = document.getElementsByClassName("phrase-line");

    let phrases = [];
    for (const phrase_line of phrase_lines) {
        phrases.push(phrase_line.childNodes[0].value);
    }
    if (phrases.length == 0){
        alert("You haven't any phrase")
        return
    }

    let entities = {};
    for (const role of project_data.entities){
        const entity_lines = document.getElementsByClassName(`${role}-line`);
        if (entity_lines.length == 0) continue;

        entities[role] = [];
        for (const entity of entity_lines){
            entities[role].push({
                text: entity.childNodes[0].value,
                value: entity.childNodes[1].value
            });
        }
    }

    const form = {
        classification: intent,
        texts: phrases,
        entitys: entities
    }

    fetch(`/api/add-template-element/${project_name}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
    })

    document.getElementById("classification").value = "";
    document.querySelectorAll(".phrase-line").forEach(el => el.remove());
    document.querySelectorAll(".template-entity-line").forEach(el => el.remove());
}
