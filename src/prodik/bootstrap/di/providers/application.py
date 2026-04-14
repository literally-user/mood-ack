from dishka import Provider, Scope, WithParents, provide_all

from prodik.application.auth import OAuthLoginInteractor
from prodik.application.task.moderation import CancelTaskInteractor
from prodik.application.task.query import (
    GetAllTasksByUserInteractor,
    GetAllTasksInteractor,
    GetTaskInteractor,
)
from prodik.application.user.command import (
    ChangePasswordInteractor,
    LoginInteractor,
    ProcessFileInteractor,
    ProcessRawInteractor,
    RegisterInteractor,
    UpdateCurrentProfileInteractor,
    UpdateProfileInteractor,
)
from prodik.application.user.moderation import (
    ActivateUserInteractor,
    DeactivateUserInteractor,
)


class ApplicationProvider(Provider):
    provides = provide_all(
        WithParents[OAuthLoginInteractor],
        WithParents[CancelTaskInteractor],
        WithParents[GetAllTasksByUserInteractor],
        WithParents[GetAllTasksInteractor],
        WithParents[GetTaskInteractor],
        WithParents[ChangePasswordInteractor],
        WithParents[LoginInteractor],
        WithParents[RegisterInteractor],
        WithParents[ProcessFileInteractor],
        WithParents[ProcessRawInteractor],
        WithParents[UpdateCurrentProfileInteractor],
        WithParents[UpdateProfileInteractor],
        WithParents[DeactivateUserInteractor],
        WithParents[ActivateUserInteractor],
        scope=Scope.REQUEST,
    )
