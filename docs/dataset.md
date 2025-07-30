# Dataset types
AI-phrase-classifier is based on artificial intelligence technologies, in particular on artificial neural networks and machine learning algorithms. The classifier is trained on a dataset that is stored in json format, the dataset can be edited both manually and through a [graphical interface](https://github.com/kretoffer/AI-phrase-classifier/tree/main/docs/guide.md).

The classifier dataset is divided into two parts and looks like this:
```json
{
    "hand-data": [], // hand part of the dataset
    "template-data": [] // template part of the dataset
}
```
Each part of the dataset is an array of data for training.
## Hand part of the dataset
The hand-data array consists of dictionaries of the following type:
#### Dataset element example
Entity: nika
```json
{
    "text": "what is a Nika", // Phrase
    "classification": "about_entity", // Message class
    "slots": [ // Slots (entities)
        {
            "entity": "rrel_entity", // Entity class
            "start": 10, // entity start character
            "end": 15 // entity end character
        }
    ]
}
```
### Slots
The phrase in the dataset must be written in lower case and without special characters. Each slot is a separate entity, there can be one slot, but there can also be many of them. The slot consists of the entity class, the beginning of the entity, and the end of the entity. If the first one is clear, then the beginning and end of the entity are the numbers of the characters in which the beginning and end of the entity are located (the characters start counting from 0). If the entity is several words, then the rules are exactly the same.
#### Example of a dataset element, with an entity that spans multiple words
Entity: Pythagorean theorem
```json
{
    "text": "tell me the pythagorean theorem", // Phrase
    "classification": "about_entity", // Message class
    "slots": [ // Slots (entities)
        {
            "entity": "rrel_entity", // Entity class
            "start": 12, // entity start character
            "end": 31 // entity end character
        }
    ]
}
```
#### Example of a dataset element with multiple entities
Entity rrel_entity: footer
Entity rrel_color: 565656
```json
{
    "text": "change footer color to 565656", // Phrase
    "classification": "about_entity", // Message class
    "slots": [ // Slots (entities)
        {
            "entity": "rrel_entity", // Enity class
            "start": 7, // entity start character
            "end": 13 // entity end character
        },
        {
            "entity": "rrel_color", // Enity class
            "start": 23, // entity start character
            "end": 29 // entity end character
        }
    ]
}
```
## Template part of the dataset
The template-data array consists of dictionaries of the form:
#### Example of a dataset element
```json
{
    "classification": "about_entity", // Message class
    "texts": [ // Array of phrase templates with variables
        "tell me the $rrel_entity"
    ],
    "entitys": { // Entities (variables in a phrase)
        "rrel_entity": [
            {
                "text": "pythagorean theorem", // The value that will be substituted into the phrase in place of the corresponding variable
                "value": "pythagorean theorem" // The value that the classifier will return
            },
            {
                "text": "axiom of lines", // The value that will be substituted into the phrase in place of the corresponding variable
                "value": "axiom of lines" // The value that the classifier will return
            }
        ]
    }
}
```
#### The same example if it were written in the manual part
```json
dataset.json
{
    "hand-data": [
        {
            "text": "tell me the pythagorean theorem", 
            "classification": "about_entity", 
            "slots": [ 
                {
                    "entity": "rrel_entity", 
                    "tokens": [ 
                        3,
                        4
                    ]
                }
            ]
        }
        {
            "text": "tell me the axiom of lines", 
            "classification": "about_entity", 
            "slots": [ 
                {
                    "entity": "rrel_entity", 
                    "tokens": [ 
                        3,
                        4,
                        5
                    ]
                }
            ]
        }
    ],
    "template-data":[]
}
```

#### Example of a dataset element with multiple entities
``` json
{
    "classification": "color_message",
    "texts": [
        "change the $rrel_entity color to $rrel_color"
    ],
    "entitys": {
        "rrel_entity": [
            {
                "text": "body",
                "value": "body"
            },
            {
                "text": "header",
                "value": "header"
            }
        ],
        "rrel_color": [
            {
                "text": "3f3f3f",
                "value": "#3f3f3f"
            },
            {
                "text": "888888",
                "value": "#888888"
            }
        ]
    }
}
```
This example is equivalent to four phrases:
- Change the body color to #3f3f3f
- Change the body color to #888888
- Change the header color to #3f3f3f
- Change the header color to #888888

# Example of a dataset element without entities
```json
{
    "classification": "greeting",
    "texts": [
        "hello",
        "hi",
        "hey"
    ],
    "entitys": {}
}
```

# Synonyms
If the entity name does not match the entity in the phrase, for example the phrase says "change footer color to 565656", and we want to get the essence "#565656", synonyms come to the rescue. There is a synonyms file in the project folder ```sinonimz.json```. So that the classifier instead "565656" issued a entity "#565656", need to add to the synonyms file the entry ```"565656": "#565656"```. The first element is what is in the phrase, and the second is what we want to see. The first element must be in lower case and without special characters, the second element can have capital letters and special characters. Synonyms in the template part of the dataset are added automatically.