import abc
import typing
import secrets
import datetime
from uuid import UUID, uuid4
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.pagination import Pagination
from core.constants.permissions import CAN_VIEW_ALL_TENANT, CAN_UPDATE_USER_EMAIL
from core.constants.roles import ADMIN
from accounts.user.domain import models as user_domain
from core.exceptions import NotFoundException, AlreadyExistsException, ForbiddenException, InvalidStateTransitionException, TokenExpiredException
from accounts.role_permission.application.policies import TenantAccessPolicy
from accounts.user.application import dtos as user_dtos
from accounts.user.application import read_models
from core.security import AbstractPasswordHandler

class AbstractUserService(abc.ABC):

    @abc.abstractmethod
    async def list_user(self, user_filters: dict, page: int, page_size: int) -> Pagination: ...

    @abc.abstractmethod
    async def retrieve_user(self, user_id: UUID) -> read_models.UserReadModel: ...

    @abc.abstractmethod
    async def add_user_to_tenant(self, data: typing.Dict) -> None: ...
    
    @abc.abstractmethod
    async def request_user_email_change(self, email_change: user_dtos.RequestUserEmailChangeDTO) -> None: ...

    @abc.abstractmethod
    async def handle_user_email_change_request(self, user_dto: user_dtos.HandleUserEmailChangeRequestDTO) -> None: ...

    @abc.abstractmethod
    async def create_user(self, data: dict) -> None:...

    @abc.abstractmethod
    async def update_user_name(self, user_dto: user_dtos.UpdateUserNameDTO, user_id: UUID | None = None) -> None: ...

    @abc.abstractmethod
    async def update_user_status(self, user_dto: user_dtos.UpdateUserStatusDTO) -> None: ...

    @abc.abstractmethod
    async def update_user_email(self, new_email_verification_token: str) -> None: ...

    @abc.abstractmethod
    async def update_user_role(self, update_role: user_dtos.UpdateRoleDTO) -> None: ...

    @abc.abstractmethod
    async def remove_user_from_tenant(self, user_id: UUID, tenant_id: UUID | None = None): ...

    @abc.abstractmethod
    async def delete_user(self, user_id: UUID): ...


class UserService(AbstractUserService):


    def __init__(self, uow: UnitOfWork, tenant_access_policy: TenantAccessPolicy, current_user: CurrentUser, password_handler: AbstractPasswordHandler):
        self._uow = uow
        self._current_user = current_user
        self._tenant_access_policy = tenant_access_policy
        self._password_handler = password_handler


    async def list_user(self, user_filters: dict, page: int, page_size: int) -> Pagination:

        
        if not user_filters.get("tenant_id"):
            if not self._current_user.is_staff:
                user_filters["tenant_id"] = self._current_user.tenant_id
                user_filters["is_staff"] = False
        else:
            self._tenant_access_policy.ensure_user_in_tenant(user_filters.get("tenant_id"))
        
        offset = (page - 1) * page_size

        total_count, users = await self._uow.user_repository.list_user(
            user_filters=user_filters,
            limit=page_size,
            offset=offset,
        )

        return Pagination(
            page=page,
            page_size=page_size,
            total=total_count,
            data=users
        )

    async def retrieve_user(self, user_id: UUID, tenant_id: UUID | None = None) -> read_models.UserReadModel:

        user = await self._uow.user_repository.get_user_with_role(
            user_id=user_id, 
            tenant_id=self._current_user.tenant_id if not tenant_id else tenant_id
        )
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    async def _create_user(self, data: dict) -> user_domain.UserModel:
        user = user_domain.UserModel.create(
            user_id=uuid4(),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email"),
            hashed_password=self._password_handler.hash_password(uuid4().hex),
            is_active=False,
            is_deleted=False,
            is_staff= data.get("is_staff") if self._current_user.is_staff else False,
            verification_token=secrets.token_urlsafe(32),
            verification_token_created_at=datetime.datetime.now(tz=datetime.timezone.utc)
        )
        await self._uow.user_repository.create_user(user=user)
        self._uow.register_entity(user)
        return user


    async def _update_deleted_user(self, data: dict) -> user_domain.UserModel:
        user = user_domain.UserModel.create(
            user_id= data.get("id"),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email"),
            hashed_password=self._password_handler.hash_password(uuid4().hex),
            is_active=False,
            is_deleted=False,
            is_staff= data.get("is_staff") if self._current_user.is_staff else False,
            verification_token=secrets.token_urlsafe(32),
            verification_token_created_at=datetime.datetime.now(tz=datetime.timezone.utc)
        )
        await self._uow.user_repository.update_user(user=user)
        self._uow.register_entity(user)
        return user

    async def create_user(self, data: dict) -> None:
        email = data.get("email", "").strip()
        existing_user = await self._uow.user_repository.get_by_email(email=email)

        if existing_user and not existing_user.is_deleted:
            raise AlreadyExistsException("User whith this email already exists")
        if existing_user and existing_user.is_deleted:
            data["id"] = existing_user.id
            user = await self._update_deleted_user(data)
        else:
            user = await self._create_user(data)
        if user.is_staff:
            user_tenant = user_domain.UserTenantModel.create_for_staff(
                role_id=data.get("role_id"),
                user_id=user.id,
                created_by_id=self._current_user.id
            )
            self._uow.user_repository.add_user_to_tenant(user_tenant)


    async def add_user_to_tenant(self, data: dict) -> None:
        
        email = data.get("email", "").strip()
        tenant_id = self._current_user.tenant_id if not data.get("tenant_id") else data.get("tenant_id")
        role_id = data.get("role_id")

        user = await self._uow.user_repository.get_by_email(email)
        
        
        existing_tenant = await self._uow.tenant_repository.get_tenant_by_id(tenant_id=tenant_id)
        
        if not existing_tenant:
            raise NotFoundException(f"Tenant with id {tenant_id} not found")

        await self._tenant_access_policy.ensure_user_in_tenant(tenant_id)

        if user and user.is_deleted:
            data["id"] = user.id
            user = await self._update_deleted_user(data)
        elif not user:
            user = await self._create_user(data)

        
        user_tenant = user_domain.UserTenantModel.create(
            email=email,
            role_id=role_id,
            tenant_id=tenant_id,
            user_id=user.id,
            tenant_name=existing_tenant.name,
            tenant_code=existing_tenant.code,
            created_by_id=self._current_user.id
        )

        if await self._uow.user_repository.user_exists_in_tenant(user.id, tenant_id):
            raise AlreadyExistsException("User already exists in tenant")

        if not  await self._uow.role_permission_repository.role_id_exists_in_tenant(role_id=role_id, tenant_id=tenant_id):
            raise NotFoundException(f"Role with id {role_id} not found in tenant with id {tenant_id}")

        await self._uow.user_repository.add_user_to_tenant(user_tenant=user_tenant)
        self._uow.register_entity(user_tenant)

    async def request_user_email_change(self, email_change: user_dtos.RequestUserEmailChangeDTO) -> None:

        users = self._uow.user_repository.get_user_by_permission_name(CAN_UPDATE_USER_EMAIL, self._current_user.tenant_id)

        tenant = self._uow.tenant_repository.get_tenant_by_id(tenant_id=self._current_user.tenant_id)

        user_email_change_request = user_domain.EmailChangeRequestModel.create(
            old_email=self._current_user.email,
            new_email=email_change.new_email,
            send_to=[user.email for user in users],
            status=user_domain.EmailChangeRequestEnum.PENDING,
            send_by_first_name=self._current_user.first_name,
            send_by_last_name=self._current_user.last_name,
            user_id=self._current_user.id,
            tenant_code = tenant.code if tenant else None,
            tenant_id= self._current_user.tenant_id,
            tenant_name= tenant.name if tenant else None,
        )
        
        if await self._uow.user_repository.email_exists(user_email_change_request.new_email):
            raise AlreadyExistsException("This email has been used already")

        self._uow.register_entity(user_email_change_request)
        self._uow.user_repository.save_user_email_request(user_email_change_request=user_email_change_request)


    async def handle_user_email_change_request(self, user_dto: user_dtos.HandleUserEmailChangeRequestDTO) -> None:

        existing_user_email_request = await self._uow.user_repository.get_user_email_request(user_id=user_dto.user_id)

        if not existing_user_email_request:
            raise NotFoundException("User email change request not found")

        if existing_user_email_request.status != user_domain.EmailChangeRequestEnum.PENDING:
            raise InvalidStateTransitionException("User email change request is not pending")


        tenant = self._uow.tenant_repository.get_tenant_by_id(tenant_id=self._current_user.tenant_id)


        user_email_request = user_domain.EmailChangeRequestModel.update(
            email_change_request_id=existing_user_email_request.id,
            old_email=existing_user_email_request.old_email,
            new_email=existing_user_email_request.new_email,
            status= user_domain.EmailChangeRequestEnum.APPROVED if user_dto.is_approved else user_domain.EmailChangeRequestEnum.REJECTED,
            send_to=existing_user_email_request.new_email if user_dto.is_approved else existing_user_email_request.old_email,
            user_id=existing_user_email_request.user_id,
            send_by_first_name=self._current_user.first_name,
            send_by_last_name=self._current_user.last_name,
            new_email_verification_token=secrets.token_urlsafe(32),
            new_email_verification_token_created_at=datetime.datetime.now(tz=datetime.timezone.utc),
            tenant_code = tenant.code if tenant else None,
            tenant_id= self._current_user.tenant_id,
            tenant_name= tenant.name if tenant else None,
        )

        self._uow.register_entity(user_email_request)
        await self._uow.user_repository.save_user_email_request(user_email_request=user_email_request)


    async def update_user_name(self, user_dto: user_dtos.UpdateUserNameDTO, user_id: UUID | None = None) -> read_models.UserReadModel:

        user_id = self._current_user.id if user_id is None else user_id

        if await self._uow.user_repository.is_user_in_tenant(user_id=user_id, tenant_id=self._current_user.tenant_id) is False:
            raise NotFoundException(f"User with id {user_id} not found")


        await self._uow.user_repository.update_user_profile(
            user_id=user_id,
            first_name=user_dto.first_name,
            last_name=user_dto.last_name
        )

        return await self._uow.user_repository.get_user_with_role(
            user_id=user_id, 
            tenant_id=self._current_user.tenant_id
        )


    async def update_user_status(self, user_dto: user_dtos.UpdateUserStatusDTO) -> None:

        if not await self._uow.user_repository.is_user_in_tenant(user_id=user_dto.user_id, tenant_id=self._current_user.tenant_id):
            raise NotFoundException(f"User with id {user_dto.user_id} not found")

        await self._uow.user_repository.update_user_status(
            user_id=user_dto.user_id,
            is_active=user_dto.is_active
        )


    async def update_user_email(self, new_email_verification_token: str) -> None:

        existing_user_email_request = await self._uow.user_repository.get_user_email_request_by_token(new_email_verification_token=new_email_verification_token)

        if existing_user_email_request is None:
            raise NotFoundException("User email change request not found")

        user_email_request = user_domain.EmailChangeRequestModel.verify(
            email_change_request_id=existing_user_email_request.id,
            old_email=existing_user_email_request.old_email,
            new_email=existing_user_email_request.new_email,
            status= existing_user_email_request.status,
            send_to=existing_user_email_request.new_email,
            user_id=existing_user_email_request.user_id,
            new_email_verification_token=existing_user_email_request.new_email_verification_token,
            new_email_verification_token_created_at=existing_user_email_request.new_email_verification_token_created_at
        )

        if user_email_request.is_expired:
            raise TokenExpiredException("User email change token has been expired")


        self._uow.register_entity(user_email_request)
        self._uow.user_repository.update_user_email(user_email_request.user_id, user_email_request.new_email)


    async def update_user_role(self, update_role: user_dtos.UpdateRoleDTO) -> None:

        existing_user = await self._uow.user_repository.get_user_with_role(user_id=update_role.user_id)
        tenant_id = update_role.tenant_id if update_role.tenant_id else self._current_user.tenant_id

        if existing_user.is_staff:
            await self._uow.user_repository.update_all_assigned_tenant_role(update_role.user_id, update_role.role_id)
        else:
            await self._uow.user_repository.update_assigned_tenant_role(update_role.user_id, update_role.role_id, tenant_id)



    async def remove_user_from_tenant(self, user_id: UUID, tenant_id: UUID | None = None) -> None:

        tenant_id = self._current_user.tenant_id if not tenant_id else tenant_id
        
        if not await self._uow.tenant_repository.tenant_id_exists(tenant_id=tenant_id):
            raise NotFoundException(f"Tenant with id {tenant_id} not found")

        self._tenant_access_policy.ensure_user_in_tenant(tenant_id)


        await self._uow.user_repository.remove_user_from_tenant(user_id=user_id, tenant_id=tenant_id)

    
    async def delete_user(self, user_id: UUID) -> None:

        await self._uow.user_repository.delete_user(user_id)
        await self._uow.user_repository.remove_user_from_all_tenant(user_id = user_id)

    async def _is_last_admin(self, exclude_id: UUID) -> True:

        if await self._uow.user_repository.get_role_count_by_name(role_name=ADMIN, tenant_id=self._current_user.tenant_id, exclude_id=exclude_id) == 0:
            return True
        return False


