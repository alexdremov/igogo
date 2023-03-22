# igogo 🐎🏎️

---

Execute several jupyter cells at the same time

> Have you ever just sited and watched a long-running jupyter cell?
> **Now, you can continue to work in the same notebook freely**

## Wait, isn't it just a background job? No.

- No multithreading, no data races, no locks.
You can freely operate with your notebook variables without the risk of corrupting them.
- Beautiful output. When several cells execute in parallel,
all printed data is displayed in corresponding cell's output. No more twisted and messed out concurrent outputs.
- Easily cancel jobs, wait for completion, and start the new ones.

## Use cases
1) You have a long-running cell, and you need to check something.
   You can just start the second cell without interrupting a long-running cell.
   > **Example:** you run a machine learning train loop and want to immediately save model's weights or check metrics.
   > With `igogo` you can do so without interrupting the training.
2) If you need to compare score of some function with different parameters, you can run several
   functions at the same time and monitor results. 
   > **Example:** you have several sets of hyperparameters and want to compare them.
   > You can start training two models, monitoring two loss graphs at the same time. 

## Install

Igogo is available through PyPi:

```bash
pip install igogo
```

## Usage
