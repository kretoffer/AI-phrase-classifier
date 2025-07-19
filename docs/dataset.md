# Dataset types
AI-phrase-classifier is based on artificial intelligence technologies, in particular on artificial neural networks and machine learning algorithms. The classifier is trained on a dataset that is stored in json format, the dataset can be edited both manually and through a [graphical interface](https://github.com/kretoffer/AI-phrase-classifier/tree/main/docs/training_quide.md).

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
            "tokens": [ // Tokens that contain the entity
                3
            ]
        }
    ]
}
```
### Slots
The phrase in the dataset must be written in lower case and without special characters. Each slot is a separate entity, there can be one slot, but there can also be many of them. The slot consists of an entity class and tokens. If the first one is clear, then tokens are the numbers of words in which the entity is located (words start from 0). So, the zero word is *what*, the first is *is*, the second is *a*, the third (entity) is *Nika*. If the entity is several words, then there can be several tokens.
#### Example of a dataset element, with an entity that spans multiple words
Entity: Pythagorean theorem
```json
{
    "text": "tell me the pythagorean theorem", // Phrase
    "classification": "about_entity", // Message class
    "slots": [ // Slots (entities)
        {
            "entity": "rrel_entity", // Entity class
            "tokens": [ // Tokens that contain the entity
                3,
                4
            ]
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
            "tokens": [ // Tokens that contain the entity
                1
            ]
        },
        {
            "entity": "rrel_color", // Enity class
            "tokens": [ // Tokens that contain the entity
                4
            ]
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
At the moment, the template part of the dataset can only work with one entity and does not work without entities. *Will be fixed in the next updates*
# Synonyms
If the entity name does not match the entity in the phrase, for example the phrase says "change footer color to 565656", and we want to get the essence "#565656", synonyms come to the rescue. There is a synonyms file in the project folder ```sinonimz.json```. So that the classifier instead "565656" issued a entity "#565656", need to add to the synonyms file the entry ```"565656": "#565656"```. The first element is what is in the phrase, and the second is what we want to see. The first element must be in lower case and without special characters, the second element can have capital letters and special characters.