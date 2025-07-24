const input = document.getElementById("text");
const modal = document.getElementById("modal");

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

export function delete_slot(ev){
    const line = ev.target.parentElement;
    line.remove();
}

export async function extract_entity(ev) {
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
    const delete_button = document.createElement("button");
    delete_button.textContent = "X";
    delete_button.onclick = delete_slot;
    delete_button.classList.add("entity-delete");
    entity_line.appendChild(delete_button);

    entities_list.appendChild(entity_line);

    document.getElementById("modal").style.display = "none";
}