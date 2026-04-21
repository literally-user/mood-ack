from dishka import Provider, Scope, provide_all

from prodik.application.auth import OAuthLoginInteractor, RefreshTokenInteractor
from prodik.application.model.command import ProcessFileInteractor, ProcessRawInteractor
from prodik.application.model.query import GetPredictingModelInfoInteractor
from prodik.application.task.moderation import CancelTaskInteractor
from prodik.application.task.query import (
    GetAllTasksByUserInteractor,
    GetAllTasksInteractor,
    GetTaskInteractor,
)
from prodik.application.user.command import (
    ChangePasswordInteractor,
    LoginInteractor,
    RegisterInteractor,
    UpdateCurrentProfileInteractor,
    UpdateProfileInteractor,
)
from prodik.application.user.moderation import (
    ActivateUserInteractor,
    DeactivateUserInteractor,
)
from prodik.application.user.query import (
    GetAllUsersInteractor,
    GetCurrentProfileInteractor,
    GetUserProfileInteractor,
)


class ApplicationProvider(Provider):
    provides = provide_all(
        GetPredictingModelInfoInteractor,
        GetAllUsersInteractor,
        GetCurrentProfileInteractor,
        GetUserProfileInteractor,
        OAuthLoginInteractor,
        CancelTaskInteractor,
        GetAllTasksByUserInteractor,
        GetAllTasksInteractor,
        GetTaskInteractor,
        ChangePasswordInteractor,
        LoginInteractor,
        RegisterInteractor,
        ProcessFileInteractor,
        ProcessRawInteractor,
        UpdateCurrentProfileInteractor,
        UpdateProfileInteractor,
        DeactivateUserInteractor,
        ActivateUserInteractor,
        RefreshTokenInteractor,
        scope=Scope.REQUEST,
    )
