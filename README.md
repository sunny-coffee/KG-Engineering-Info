# KG-Engineering-Info

## python version = 3.7.9
It is recommended to manange environments with Anaconda.
```bash
conda create --name thesis_env python=3.7
conda activate thesis_env
```

## install camelot-py  version = 0.8.2
```bash
pip install "camelot-py[cv]"
```

if there is the issue "RuntimeError: Please make sure that Ghostscript is installed", when camelot.read_pdf() runs, please  installed Ghostscript installer from this Website: https://www.ghostscript.com/download/gsdnld.htm.

## install owlready2  version = 0.26
```bash
pip install Owlready2
```

## install spacy  version = 2.3.5
```bash
pip install spacy
```

## install English medium model  version = 2.3.1
```bash
python -m spacy download en_core_web_md
```

## install English small model  version = 2.3.1
```bash
python -m spacy download en_core_web_sm
```

## install neuralcoref  version = 4.0
since Neuralcoref collide with Spacy with higher version, it is better to install NeuralCoref from source.
```bash
git clone https://github.com/huggingface/neuralcoref.git
cd neuralcoref
pip install -r requirements.txt
pip install -e .
```

## install Allennlp and its model version = 1.4.0
```bash
pip install allennlp
pip install --pre allennlp-models
```
