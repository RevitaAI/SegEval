# SegEval
A python re-implementation of "A Novel Evaluation Method for Morphological Segmentation"


```bash

python3 evaluator.py --gold <gold.txt> --pred <pred.txt> --theories <theories.txt>

```

### Dependencies
- Python 3.10+
- sklearn

### Reference

```bibtex
@inproceedings{nouri-yangarber-2016-novel,
    title = "A Novel Evaluation Method for Morphological Segmentation",
    author = "Nouri, Javad  and
      Yangarber, Roman",
    editor = "Calzolari, Nicoletta  and
      Choukri, Khalid  and
      Declerck, Thierry  and
      Goggi, Sara  and
      Grobelnik, Marko  and
      Maegaard, Bente  and
      Mariani, Joseph  and
      Mazo, Helene  and
      Moreno, Asuncion  and
      Odijk, Jan  and
      Piperidis, Stelios",
    booktitle = "Proceedings of the Tenth International Conference on Language Resources and Evaluation ({LREC}'16)",
    month = may,
    year = "2016",
    address = "Portoro{\v{z}}, Slovenia",
    publisher = "European Language Resources Association (ELRA)",
    url = "https://aclanthology.org/L16-1495/",
    pages = "3102--3109",
    abstract = "Unsupervised learning of morphological segmentation of words in a language, based only on a large corpus of words, is a challenging task. Evaluation of the learned segmentations is a challenge in itself, due to the inherent ambiguity of the segmentation task. There is no way to posit unique ``correct'' segmentation for a set of data in an objective way. Two models may arrive at different ways of segmenting the data, which may nonetheless both be valid. Several evaluation methods have been proposed to date, but they do not insist on consistency of the evaluated model. We introduce a new evaluation methodology, which enforces correctness of segmentation boundaries while also assuring consistency of segmentation decisions across the corpus."
}
```
