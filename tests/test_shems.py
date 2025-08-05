from src.shemes import UpdateDatasetFormData, DatasetData, FormSlot, Slot

def test_dataset_form_data_to_dataset_data():
    dataset_form = UpdateDatasetFormData(text="hello", classification="greeting", slots=[])
    result = DatasetData(text="hello", classification="greeting", slots=[])
    assert dataset_form.to_dataset_data() == (result, {})
    dataset_form.text = "HeLLo!"
    assert dataset_form.to_dataset_data() == (result, {})
    form_slot = FormSlot(entity="rrel_entity", start=0, end=5, value="HeLLo")
    slot = Slot(entity="rrel_entity", start=0, end=5)
    dataset_form.slots.append(form_slot)
    result.slots.append(slot)
    assert dataset_form.to_dataset_data() == (result, {})
    dataset_form.slots[0].value = "HELLO"
    assert dataset_form.to_dataset_data() == (result, {"hello": "HELLO"})
