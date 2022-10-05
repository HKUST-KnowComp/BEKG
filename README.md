# BEKG
#### Source Code for paper: BEKG: A Built Environment Knowledge Graph
## Table of Contents

- [Background](#Background)
- [Code and Model](https://github.com/HKUST-KnowComp/BEKG/blob/main/README.md#code--model)
- [Data](#Data)
- [Contributing](#Contributing)
- [License](#License)
## Background
Practices in the built environment have become more digitalized with the rapid development of modern design and construction technologies. However, the requirement of practitioners or scholars to gather complicated professional knowledge in the built environment has not been satisfied yet. In this paper, more than 80,000 paper abstracts in the built environment field were obtained to build a knowledge graph, a knowledge base storing entities and their connective relations in a graph-structured data model. To ensure the retrieval accuracy of the entities and relations in the knowledge graph, two well-annotated datasets have been created, containing 2,000 instances and 1,450 instances each in 29 relations for the named entity recognition task and relation extraction task respectively. These two tasks were solved by two BERT-based models trained on the proposed dataset. Both models attained an accuracy above 85% on these two tasks. More than 200,000 high-quality relations and entities were obtained using these models to extract all abstract data. Finally, this knowledge graph is presented as a self-developed visualization system to reveal relations between various entities in the domain.
## Code & Model
### BERT-Pair
* #### Codes in folder [Codes/BERT-Pair](https://github.com/HKUST-KnowComp/BEKG/tree/main/Codes/BERT-Pair)
* #### Checkpoint [Google Drive](https://drive.google.com/file/d/1R8GY4Pv_4ikfcCWKXVAKg97frN1G_oMI/view?usp=sharing)
### BERT-CRF
* #### Codes in folder [Codes/BERT-CRF](https://github.com/HKUST-KnowComp/BEKG/tree/main/Codes/BERT-CRF)
* #### Checkpoint [Google Drive](https://drive.google.com/file/d/1jxsxW9e_pRG3bbp-Dsd_IWbeQPq4oZLT/view?usp=sharing)
## Data
### Raw Data:
* #### Abstracts Obtained from Microsoft Academic Graph [[Google Drive](https://drive.google.com/file/d/19RG_geazLt9be3zU2knRkLQPfxZSkf4X/view?usp=sharing) , [Baidu Drive](https://pan.baidu.com/s/1ChABm0aI38vYN69jGfARZg) (code: 03df)]
### Annotation Data on the Brat:
* #### Annotation for Relation Extraction Dataset [Google Drive](https://drive.google.com/drive/folders/1znsk-HCkqlWeSYi357pLTCeTlr8xuAY6?usp=sharing)
* #### Annotation for Human Checkout [Google Drive](https://drive.google.com/drive/folders/1VAbxeRk4zJ5-xVFAogDWgf5got1VqFOY?usp=sharing)
### Data in Named Entity Recognition task:
* #### Dataset in folder [Data/Dataset/Named Entity Recognition](https://github.com/HKUST-KnowComp/BEKG/tree/main/Data/Dataset/Named%20Entity%20Recognition)
* #### Results [Google Drive](https://drive.google.com/drive/folders/1PxNauFn-xeTVMYc8PCDucZMiPznmBFXe?usp=sharing)
### Data in Relation Extraction task:
* #### Dataset in folder [Data/Dataset/Relation Extraction](https://github.com/HKUST-KnowComp/BEKG/tree/main/Data/Dataset/Relation%20Extraction)
* #### Results in folder [Data/Extraction](https://github.com/HKUST-KnowComp/BEKG/tree/main/Data/Extraction)
## Contributing
## License
