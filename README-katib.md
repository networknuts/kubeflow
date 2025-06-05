
# 🎯 Katib Hyperparameter Tuning: Fashion MNIST

This lab demonstrates how to use **Katib** (Kubeflow's AutoML system) to perform **hyperparameter tuning** on a simple image classification task using the **Fashion MNIST** dataset.

---

## 📁 Project Structure

```
katib-fashion-mnist/
├── train.py                 # Model training script
├── Dockerfile               # Docker image for Katib to run
├── katib-experiment.yaml    # KatibExperiment CRD with tuning config
```

---

## 🧠 Objective

We want to automatically find the best values for the following hyperparameters to **maximize model accuracy**:

- `LEARNING_RATE`: how fast the model learns
- `EPOCHS`: how many times the model sees the training data
- `BATCH_SIZE`: number of images processed at once

---

## 🛠️ Steps to Run

### 1. 🔨 Build and Push Docker Image

```bash
docker build -t <your-registry>/fashion-mnist-tuner:latest .
docker push <your-registry>/fashion-mnist-tuner:latest
```

Make sure to update the `image:` field in `katib-experiment.yaml` accordingly.

---

### 2. 🚀 Run the Katib Experiment

```bash
kubectl apply -f katib-experiment.yaml -n kubeflow-user-example-com
```

You can modify the namespace if you're using a different profile.

---

### 3. 📊 Monitor Progress

Visit the **Katib UI** inside your Kubeflow Dashboard:

- Navigate to Experiments
- Click on `fashion-mnist-random-tuning`
- View parallel trials, metrics, and best results

---

## 🔬 What's Being Tuned

```yaml
parameters:
  - name: LEARNING_RATE   # float: 0.0001–0.01
  - name: EPOCHS          # int: 3–10
  - name: BATCH_SIZE      # int: 32–128
```

Katib runs multiple training jobs (trials) using random values for these parameters, and logs their `accuracy` from `train.py`.

---

## ✅ Output

You’ll get:
- A list of trials with accuracy for each hyperparameter combo
- The best-performing trial with its parameter set
- Logs for each trial job in Kubeflow UI

---

## 📦 Bonus Ideas

- Swap in **Bayesian optimization** instead of random
- Use **TensorBoard** for visualization
- Add **early stopping criteria**
- Extend the script for **model export** to MinIO or PVC

---

Created for educational purposes. Happy tuning!
