from dishka import Provider, Scope, provide_all

from prodik.application.authorization import (
    ChangePasswordInteractor,
    LoginInteractor,
    OAuthLoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
)
from prodik.application.content_processing import (
    ProcessFileInteractor,
    ProcessRawInteractor,
)
from prodik.application.manage_profile import (
    UpdateCurrentProfileInteractor,
    UpdateProfileInteractor,
)
from prodik.application.manage_task import CancelTaskInteractor
from prodik.application.manage_user import (
    ActivateUserInteractor,
    DeactivateUserInteractor,
)
from prodik.application.receive_model_info import GetPredictingModelInfoInteractor
from prodik.application.receive_task_info import (
    GetAllTasksByUserInteractor,
    GetAllTasksInteractor,
    GetTaskInteractor,
)
from prodik.application.receive_upload_link import GetFileStorageLinkInteractor
from prodik.application.receive_user_info import (
    GetAllUsersInteractor,
    GetCurrentProfileInteractor,
    GetUserProfileInteractor,
)
from prodik.application.services import SessionService


class ApplicationProvider(Provider):
    provides = provide_all(
        SessionService,
        GetFileStorageLinkInteractor,
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
