import asyncio
from typing import Literal, List, Dict

from fastapi import APIRouter, HTTPException
from app.engine import get_agent_runner
from app.api.routers.types import (
    _ChatMessage,
    _TaskStepOutput,
    _TaskStep,
    _TaskSate,
    _Task,
)

agent_router = r = APIRouter()

agent = get_agent_runner()

# global state
running = False
stepwise = False
step_interval = 5


async def worker() -> None:
    """Worker function that runs the agent in the background."""
    global running
    global stepwise
    global step_interval

    while True:
        if not running:
            await asyncio.sleep(step_interval)
            continue

        current_tasks = agent.list_tasks()
        current_task_ids = [task.task_id for task in current_tasks]

        completed_tasks = agent.get_completed_tasks()
        completed_task_ids = [task.task_id for task in completed_tasks]

        for task_id in current_task_ids:
            if task_id in completed_task_ids:
                continue

            step_output = await agent.arun_step(task_id)

            if step_output.is_last:
                agent.finalize_response(task_id, step_output=step_output)

        if stepwise:
            running = False

        await asyncio.sleep(step_interval)


@r.post("/tasks", tags=["tasks"])
async def create_task(input: str) -> _Task:
    task = agent.create_task(input)

    return _Task.from_task(task)


@r.get("/tasks", tags=["tasks"])
async def get_tasks() -> List[_Task]:
    tasks = agent.list_tasks()

    _tasks = []
    for task in tasks:
        _tasks.append(_Task.from_task_state(task))

    return _tasks


@r.get("/tasks/state/{task_id}", tags=["tasks"])
async def get_task(task_id: str) -> _TaskSate:
    task_state = agent.state.task_dict.get(task_id)
    if task_state is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return _TaskSate.from_task_state(task_state)


@r.get("/tasks/completed", tags=["tasks"])
async def get_completed_tasks() -> List[_Task]:
    completed_tasks = agent.get_completed_tasks()

    _completed_tasks = []
    for task in completed_tasks:
        _completed_tasks.append(_Task.from_task(task))

    return _completed_tasks


@r.get("/tasks/{task_id}/output", tags=["tasks"])
async def get_task_output(task_id: str) -> _TaskStepOutput:
    task_output = agent.get_task_output(task_id)

    return _TaskStepOutput.from_task(task_output)


@r.get("/tasks/{task_id}/upcoming_steps", tags=["task-steps"])
async def get_task_steps(task_id: str) -> List[_TaskStep]:
    task_steps = agent.get_upcoming_steps(task_id)

    steps = []
    for step in task_steps:
        steps.append(_TaskStep.from_task_step(step))

    return steps


@r.get("/tasks/{task_id}/completed_steps", tags=["task-steps"])
async def get_completed_steps(task_id: str) -> List[_TaskStepOutput]:
    completed_step_outputs = agent.get_completed_steps(task_id)

    _step_outputs = []
    for step_output in completed_step_outputs:
        _step_outputs.append(_TaskStepOutput.from_task_step_output(step_output))

    return _step_outputs


# ---- Agent Control ----


@r.get("/messages", tags=["agent-control"])
async def get_messages() -> List[_ChatMessage]:
    messages = agent.chat_history

    return [_ChatMessage.from_chat_message(message) for message in messages]


@r.post("/running", tags=["agent-control"])
async def set_worker_state(state: Literal["running", "stopped"]) -> Dict[str, bool]:
    global running
    running = state == "running"

    return {"running": running}


@r.get("/running", tags=["agent-control"])
async def get_worker_state() -> Dict[str, bool]:
    return {"running": running}


@r.post("/stepwise", tags=["agent-control"])
async def toggle_stepwise(state: Literal["on", "off"]) -> Dict[str, bool]:
    global stepwise
    stepwise = state == "on"

    return {"stepwise": stepwise}


@r.get("/stepwise", tags=["agent-control"])
async def get_stepwise_state() -> Dict[str, bool]:
    return {"stepwise": stepwise}


@r.post("/step_interval", tags=["agent-control"])
async def set_step_interval(interval: int) -> Dict[str, int]:
    global step_interval

    step_interval = interval
    return {"step_interval": step_interval}


@r.get("/step_interval", tags=["agent-control"])
async def get_step_interval() -> Dict[str, int]:
    return {"step_interval": step_interval}


@r.post("/reset", tags=["agent-control"])
async def reset_agent() -> Dict[str, str]:
    agent.reset()

    return {"message": "Agent reset"}


# Start worker on startup
def startup() -> None:
    asyncio.create_task(worker())


# Register startup function
r.on_startup.append(startup)
