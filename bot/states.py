from aiogram.fsm.state import StatesGroup, State

class EditTaskStates(StatesGroup):
    waiting_for_new_title = State()

class AddTaskStates(StatesGroup):
    waiting_for_task_text = State()
