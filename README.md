# airflow_eks

## Steps to deploy airflow on local eks

1. Download the tar chart: `wget https://dlcdn.apache.org/airflow/helm-chart/1.10.0/airflow-1.10.0.tgz`

2. Export the templates: `helm template --output-dir ./ airflow-1.10.0.tgz`

3. Create a config map to deploy the postgres database: `kubectl apply -f configmaps/postgres-configmap.yaml -n local-airflow`

4. Create the persistent volumes and the persistent volume claims: `kubectl apply -f persistent-volumes/postgres-storage.yaml -n local-airflow`
   - 4.1 Validate the volumes created: `kubectl get pv -n local-airflow && kubectl get pvc -n local-airflow`

5. Deploy the postgres db to a pod: `kubectl apply -f deployments/postgres-deployment.yaml -n local-airflow`
   - 5.1 check the deployment: `kubectl get pods -n local-airflow`

6. Create a service to expose the db: `kubectl apply -f services/postgres-service.yaml -n local-airflow`

7. Deploy the schemas and tables in the DB:
   - 7.1 Deploy the schemas and tables:
         - 7.1.1 Install python: https://tecadmin.net/how-to-install-python-3-10-on-debian-11/, change the version to 3.10.0
         - 7.1.2 Get the constraints url: `CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.6.1/constraints-3.10.txt"`
         - 7.1.3 Install the airflow postgres db tables: `pip install "apache-airflow[postgres]==2.6.1" --constraint "${CONSTRAINT_URL}"`
         - 7.1.4 Change the db connection in the airfloow.cfg file: `sql_alchemy_conn = postgresql+psycopg2://admin:test123@localhost:5432/postgresdb`
         - 7.1.5 init the postgres db: `airflow db init`
   - 7.2 Get inside the postgres database that was installed into the pod and check for the airflow tables: `kubectl exec -it postgres-6496c4d4f7-x8rkb -n local-airflow -- psql -h localhost -U admin --password -p 5432 postgresdb`

8. Create the storage for the dags and logs:
   - 8.1 Create the persistent volumes and the persistent volume claims for dags: `kubectl apply -f persistent-volumes/dags-storage.yaml -n local-airflow`
   - 8.2 Create the persistent volumes and the persistent volume claims for logs: `kubectl apply -f persistent-volumes/logs-storage.yaml -n local-airflow`

9. Create a config map to inyect config variables to airflow: `kubectl apply -f configmaps/configmap.yaml -n local-airflow`
   - 9.1 Show the config map configuration: `kubectl describe configmap airflow-config -n local-airflow`

10. Create a service account for the scheduler: `kubectl apply -f scheduler/scheduler-serviceaccount.yaml -n local-airflow`

11. Create a role: `kubectl apply -f rbac/pod-launcher-role.yaml -n local-airflow`

12. Create a role binding: `kubectl apply -f rbac/pod-launcher-rolebinding.yaml -n local-airflow`
    - 12.1 Validate the bind between the service account and the role: `kubectl auth can-i list pods --as=system:serviceaccount:local-airflow:airflow-scheduler-serviceaccount -n local-airflow`

13. Deploy the scheduler and webserver: `kubectl apply -f deployments/airflow-deployment.yaml -n local-airflow`
    - 13.1 Pod logs: `kubectl logs airflow-8cc8c598-kkchg -n local-airflow`

14. Create a service to expose the webserver: `kubectl apply -f services/airflow-service.yaml -n local-airflow`

15. Make port fordward to access to the webserver UI from your local machine: ``

16. Create a user to access to the UI: `airflow users create --e EMAIL --f FIRSTNAME --l LASTNAME --r ROLE -u USERNAME`