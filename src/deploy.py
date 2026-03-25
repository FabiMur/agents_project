import time

from bedrock_agentcore_starter_toolkit import Runtime

from config import settings
from src.utils import create_agentcore_role

region = settings.aws_region


def configure_runtime(agent_name: str, agentcore_iam_role: dict, python_file_name: str):
    agentcore_runtime = Runtime()

    response = agentcore_runtime.configure(
        entrypoint=python_file_name,
        execution_role=agentcore_iam_role["Role"]["Arn"],
        auto_create_ecr=True,
        requirements_file="requirements.txt",
        region=region,
        agent_name=agent_name,
    )
    return response, agentcore_runtime


def check_status(agent_runtime) -> str:
    status_response = agent_runtime.status()
    status = status_response.endpoint["status"]
    end_status = ["READY", "CREATE_FAILED", "DELETE_FAILED", "UPDATE_FAILED"]
    while status not in end_status:
        time.sleep(10)
        status_response = agent_runtime.status()
        status = status_response.endpoint["status"]
        print(status)
    return status


def deploy_agent(agent_name: str, python_file_name: str) -> dict:
    iam_role = create_agentcore_role(agent_name=agent_name, region=region)
    role_arn = iam_role["Role"]["Arn"]
    role_name = iam_role["Role"]["RoleName"]
    print(f"{agent_name} role ARN: {role_arn}")
    print(f"{agent_name} role name: {role_name}")

    _, runtime = configure_runtime(agent_name, iam_role, python_file_name)
    launch_result = runtime.launch()

    agent_id = launch_result.agent_id
    agent_arn = launch_result.agent_arn
    print(f"{agent_name} ARN: {agent_arn}")

    status = check_status(runtime)
    print(f"{agent_name} status: {status}")

    return {"id": agent_id, "arn": agent_arn, "role_arn": role_arn, "status": status}
