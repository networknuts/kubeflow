# Hyperparameters Tuning (Katib)
- [Hyperparameters Tuning (Katib)](#hyperparameters-tuning-katib)
  - [Example](#example)
    - [Task. Hyperparameter Search on Iris Dataset](#task-hyperparameter-search-on-iris-dataset)
    - [Required Files. Docker Image](#required-files-docker-image)
    - [Hyperparameter Search Configuration](#hyperparameter-search-configuration)
    - [Run Hyperparameter Search](#run-hyperparameter-search)
  - [GPU and Shared Memory](#gpu-and-shared-memory)

Accoring to the [official documentation](https://www.kubeflow.org/docs/components/katib/overview/), Katib is:

> Katib is a Kubernetes-native project for automated machine learning (AutoML). Katib supports hyperparameter tuning, early stopping, and neural architecture search (NAS). Learn more about AutoML at fast.ai, Google Cloud, Microsoft Azure, or Amazon SageMaker.

## Example

### Task. Hyperparameter Search on Iris Dataset

For the sake of example, we'll train and find optimal hyperparameters for a simple logistic regression model on the iris dataset.

In its simple form, training has the following form:

```python
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

iris = datasets.load_iris()
X = iris.data
y = iris.target

RANDOM_STATE = 1337
penalty = "l2"
tol = 0.001
C = 0.01
max_iter = 5

X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2,
                                                    random_state=RANDOM_STATE)
clf = LogisticRegression(penalty=penalty,
                         tol=tol,
                         C=C,
                         max_iter=max_iter,
                         random_state=RANDOM_STATE)

clf.fit(X=X_train, y=y_train)
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"accuracy={acc}")
```

We're going to find the optimal combination of the following hyperparameters:
- `penalty`
- `tol`
- `C`
- `max_iter`

The search space is as follows:

```python
penalty      = ['l2']
tol          = [0.001, 0.0001, 0.00001]
C            = [0.01, 0.50, 1.00]
max_iter     = [3, 5, 10]
```

As the optimization function (objective) we use accuracy. So, the goal is to find a combination of hyperparameters that gives maximum accuracy.

The search algorithm is `random search`. There are a lot more search algorithms available there. Please, refer to the [official documentation](https://www.kubeflow.org/docs/components/katib/experiment/#search-algorithms-in-detail) to check all of them.

Each trial of search is run in a separate container. So, we have to wrap the training code into the docker image. A new set of hyperparameters are passed via command-line arguments.

But how does Katib detect which run has better accuracy? Katib uses the `Metric Collector` concept to deal with the problem. Katib can read metric info from:
- stdout
- file
- TensorFlow Event
- Prometheus
- or any configured custom source

For simplicity, we use `stdout`. **It is important to note** that:
> Katib parses metrics in this format: `<metric-name>=<metric-value>`.

This means that in case of accuracy maximization, we have to do:

```python
print(f"accuracy={accuracy}")
```

at the end of each training and validation step.

### Required Files. Docker Image

Here we provide source code for training the iris classification model as well as the Dockerfile:
- train.py
- requirements.txt
- Containerfile

Build and push docker image:

```bash
docker build -t YOUR_REGISTRY/katib-kubeflow-tuner:latest -f ./Dockerfile .
docker push YOUR_REGISTRY/katib-kubeflow-tuner:latest
```

### Hyperparameter Search Configuration

After the training image is ready we can proceed to the hyperparameter search configuration.

To create and run Katib hyperparameter tuning we'll use Kubeflow UI. Navigate to `Katib` and press `New Experiment`.

Follow the wizard and fill in all necessary information.

1. Metadata
   - Name: `katib-experiment`
2. Trial Thresholds
   - Trial Thresholds
     - Parallel Trials: `3`
     - Max Trials: `12`
     - Max Failed Trials: `3`
     - Resume Policy: `Long Running`
3. Objective
   - Type: `Maximize`
   - Metric: `accuracy`
   - Goal: `0.99`
   - Additional Metrics: None
4. Search Algorithm
   - Hyperparameter Tuning: `yes`
   - Name: `Random`
5. Early stopping
   - Algorithm: None
6. Hyper Parameters

   - Param 1
     - Name: `penalty`
     - Type: `Categorical`
     - Values: `l2`


   - Param 2
     - Name: `tol`
     - Type: `Discrete`
     - Values:
       - `0.001`
       - `0.0001`
       - `0.00001`

   - Param 3
     - Name: `C`
     - Type: `Discrete`
     - Values:
       - `0.01`
       - `0.50`
       - `1.00`

   - Param 4
     - Name: `max_iter`
     - Type: `Discrete`
     - Values:
       - `3`
       - `5`
       - `10`



7. Metrics Collector
   - Kind: `Stdout`
8. Trial Template
   - Primary Container Name: `training-container`
   - Source Type: `YAML`
   - Paste the following configuration:

```yaml
apiVersion: batch/v1
kind: Job
spec:
  template:
    spec:
      containers:
        - name: training-container
          image: YOUR_REGISTRY/katib-kubeflow-tuner:latest
          command:
            - "python3"
            - "train.py"
            - "--penalty=${trialParameters.penalty}"
            - "--tol=${trialParameters.tol}"
            - "--C=${trialParameters.C}"
            - "--max-iter=${trialParameters.max_iter}"
      restartPolicy: Never
    metadata:
      annotations:
        sidecar.istio.io/inject: "false"
```

   - Fill references below the template:

Optionally, you can view and edit the configuration to add, for example, GPU requests for training, or specify memory limits, as well as shared memory mount.

You can save the configuration. It helps to avoid interaction with tedious wizards and paste configuration directly. As you can see, the YAML configuration contains all the settings we've set up earlier.

```yaml
apiVersion: kubeflow.org/v1beta1
kind: Experiment
metadata:
  name: katib-experiment
  namespace: ''
spec:
  maxTrialCount: 12
  parallelTrialCount: 3
  maxFailedTrialCount: 3
  resumePolicy: LongRunning
  objective:
    type: maximize
    goal: 0.99
    objectiveMetricName: accuracy
    additionalMetricNames: []
  algorithm:
    algorithmName: random
    algorithmSettings: []
  parameters:
    - name: penalty
      parameterType: categorical
      feasibleSpace:
        list:
          - l2
    - name: tol
      parameterType: categorical
      feasibleSpace:
        list:
          - '0.001'
          - '0.0001'
          - '0.00001'
    - name: C
      parameterType: discrete
      feasibleSpace:
        list:
          - '0.01'
          - '0.50'
          - '1.00'
    - name: max_iter
      parameterType: discrete
      feasibleSpace:
        list:
          - '3'
          - '5'
          - '10'
  metricsCollectorSpec:
    collector:
      kind: StdOut
  trialTemplate:
    primaryContainerName: training-container
    successCondition: status.conditions.#(type=="Complete")#|#(status=="True")#
    failureCondition: status.conditions.#(type=="Failed")#|#(status=="True")#
    retain: false
    trialParameters:
      - name: penalty
        reference: penalty
        description: ''
      - name: tol
        reference: tol
        description: ''
      - name: C
        reference: C
        description: ''
      - name: max_iter
        reference: max_iter
        description: ''
    trialSpec:
      apiVersion: batch/v1
      kind: Job
      spec:
        template:
          spec:
            containers:
              - name: training-container
                image: YOUR_REGISTRY/katib-kubeflow-tuner:latest
                command:
                  - python3
                  - train.py
                  - '--penalty=${trialParameters.penalty}'
                  - '--tol=${trialParameters.tol}'
                  - '--C=${trialParameters.C}'
                  - '--max-iter=${trialParameters.max_iter}'
            restartPolicy: Never
          metadata:
            annotations:
              sidecar.istio.io/inject: 'false'

```

### Run Hyperparameter Search

After the experiment is started you'll be redirected to the experiment list view.


Click on the experiment name to see its details and results.

On the top, there is a plot showing hyperparameters along with optimized metrics.


Down on the page, you'll find details on each trial result:

## GPU and Shared Memory

Assume for the given above example you'd like to add GPU resources. How to request resources?

Katib UI doesn't provide capabilities for resource requests. So, we have to request resources manually.

It is done by annotating the `template` section as listed below:

```yaml
apiVersion: batch/v1
kind: Job
spec:
  template:
    spec:
      # Step 1. Add toleration.
      tolerations:
        - effect: NoSchedule
          key: feature.node.kubernetes.io/type
          operator: Equal
          value: gpu
      containers:
        - name: training-container
          image: YOUR_REGISTRY/katib-kubeflow-tuner:latest
          command:
            - "python3"
            - "train.py"
            - "--penalty=${trialParameters.penalty}"
            - "--tol=${trialParameters.tol}"
            - "--C=${trialParameters.C}"
            - "--max-iter=${trialParameters.max_iter}"
          # Step 2 [OPTIONAL]. Add necessary env variabeles.
          env:
            - name: "XXXXXXXXXXXXXXXXXXXXX"
              value: "XXXXXXXXXXXXXXXXXXXXX"
            - name: "XXXXXXXXXXXXXXXXXXXXX"
              value: "XXXXXXXXXXXXXXXXXXXXX"
          # Step 3. Requests for resources.
          resources:
            limits: { nvidia.com/gpu: 1, memory: 8Gi, cpu: "2" }
            requests: { nvidia.com/gpu: 1, memory: 4Gi, cpu: "2" }
          volumeMounts:
            - { mountPath: /dev/shm, name: shm }
      # Step 4. Allocate volume for shared memory.
      volumes:
        - emptyDir: { medium: Memory }
          name: shm
      restartPolicy: Never
    metadata:
      annotations:
        sidecar.istio.io/inject: "false"
```
