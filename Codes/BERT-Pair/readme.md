# The BERT-Pair model for Relation Classification task in BEKG.

## Training a Model

To train a 5-way 1-shot models, use command bellow:

```bash
python train_demo.py \
    --trainN 5 --N 5 --K 1 --Q 1 \
    --model pair --encoder bert --pair --hidden_size 768 --val_step 1000 \
    --batch_size 4  --fp16 \
```

This will start the training and evaluating process of Prototypical Networks in a 5-way 1-shot setting. You can also use different args to start different process. Some of them are here:

> * `train / val / test`: Specify the training / validation / test set. For example, if you use `train_wiki` for `train`, the program will load `data/train_wiki.json` for training. You should always use `train_wiki` for training and `val_wiki` (FewRel 1.0 and FewRel 2.0 NOTA challenge) or `val_pubmed` (FewRel 2.0 DA challenge) for validation.
> * `trainN`: N in N-way K-shot. `trainN` is the specific N in training process.
> * `N`: N in N-way K-shot.
> * `K`: K in N-way K-shot.
> * `Q`: Sample Q query instances for each relation.
> * `model`: Which model to use. The default one is `proto`, standing for Prototypical Networks. Note that if you use the **PAIR** model from our paper [FewRel 2.0](https://www.aclweb.org/anthology/D19-1649.pdf), you should also use `--encoder bert --pair`.
> * `encoder`: Which encoder to use. You can choose `cnn` or `bert`. 
> * `na_rate`: NA rate for FewRel 2.0 none-of-the-above (NOTA) detection. Note that here `na_rate` specifies the rate between Q for NOTA and Q for positive. For example, `na_rate=0` means the normal setting, `na_rate=1,2,5` corresponds to NA rate = 15%, 30% and 50% in 5-way settings.

## Inference

You can evaluate an existing checkpoint by

```bash
python train_demo.py --only_test --load_ckpt {CHECKPOINT_PATH} {OTHER_ARGS}
```

Providing a BERT-Pair [checkpoint](https://drive.google.com/file/d/1R8GY4Pv_4ikfcCWKXVAKg97frN1G_oMI/view?usp=sharing) (trained on BEKG Few-shot Relation Classification dataset, using 5-way 1-shot setting).
