# 📦 Kubeflow Notebook Server Images

This repository provides a set of **prebuilt container images** for Kubeflow Notebooks. The images are organized into two categories:

- **Base Images**: Minimal environments (Jupyter, RStudio, VS Code).
- **Extended Images**: Real-world setups with ML frameworks, CUDA, and data science packages.

---

## 🧱 Base Images

These are minimal setups providing standard environments for various editors.

| Use Case                   | Container Image |
|----------------------------|------------------|
| Base image for all other images | `ghcr.io/kubeflow/kubeflow/notebook-servers/base` |
| VS Code editor via code-server | `ghcr.io/kubeflow/kubeflow/notebook-servers/codeserver` |
| JupyterLab environment         | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter` |
| RStudio environment            | `ghcr.io/kubeflow/kubeflow/notebook-servers/rstudio` |

---

## 🚀 Extended Kubeflow Images

These images extend base environments with frameworks like **PyTorch**, **TensorFlow**, **CUDA**, **Tidyverse**, and more.

| Use Case                                           | Container Image |
|----------------------------------------------------|------------------|
| VS Code + Conda-based Python dev environment       | `ghcr.io/kubeflow/kubeflow/notebook-servers/codeserver-python` |
| RStudio for data science with Tidyverse            | `ghcr.io/kubeflow/kubeflow/notebook-servers/rstudio-tidyverse` |
| JupyterLab with core scientific Python stack       | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-scipy` |
| JupyterLab with PyTorch                            | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-pytorch` |
| Jupyter + PyTorch + common data science libraries  | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-pytorch-full` |
| Jupyter + PyTorch + GPU support (CUDA)             | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-pytorch-cuda` |
| PyTorch + CUDA + full data science stack           | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-pytorch-cuda-full` |
| JupyterLab with TensorFlow                         | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-tensorflow` |
| TensorFlow + Jupyter + common ML libraries         | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-tensorflow-full` |
| TensorFlow + GPU (CUDA) + JupyterLab               | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-tensorflow-cuda` |
| TensorFlow + CUDA + full data science stack        | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-tensorflow-cuda-full` |
| PyTorch + Habana Gaudi accelerator support         | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-pytorch-gaudi` |
| Gaudi + PyTorch + full ML stack                    | `ghcr.io/kubeflow/kubeflow/notebook-servers/jupyter-pytorch-gaudi-full` |

---

## 📘 Notes

- All images are hosted on **GitHub Container Registry (GHCR)**.
- Fully compatible with the **Kubeflow NotebookController**.
- You can extend these images or use them as drop-in replacements in your ML workflows.


