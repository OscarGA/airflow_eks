from __future__ import annotations

import logging
import os

import pendulum

from airflow import DAG
from airflow.configuration import conf
from airflow.decorators import task
from airflow.example_dags.libs.helper import print_stuff
from airflow.operators.bash import BashOperator

log = logging.getLogger(__name__)

worker_container_repository = conf.get("kubernetes_executor", "worker_container_repository")
worker_container_tag = conf.get("kubernetes_executor", "worker_container_tag")

try:
    from kubernetes.client import models as k8s
except ImportError:
    log.warning(
        "The example_kubernetes_executor example DAG requires the kubernetes provider."
        " Please install it with: pip install apache-airflow[cncf.kubernetes]"
    )
    k8s = None


if k8s:
    with DAG(
        dag_id="example_kubernetes_executor",
        schedule=None,
        start_date=pendulum.datetime(2023, 8, 8, tz="UTC"),
        catchup=False,
        tags=["example1"],
    ) as dag:
        # You can use annotations on your kubernetes pods!
        start_task_executor_config = {
            "pod_override": k8s.V1Pod(metadata=k8s.V1ObjectMeta(annotations={"test": "annotation"}))
        }

        BashOperator(
            task_id="bash_resource_requirements_override_example",
            bash_command="echo hi from bash",
            executor_config=start_task_executor_config
        )

        @task(executor_config=start_task_executor_config)
        def start_task():
            print("hi from task")

        start_task()
