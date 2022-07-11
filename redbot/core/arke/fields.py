from typing import TYPE_CHECKING, Any, Union, Optional, Literal, Type

from tortoise import models
from tortoise.fields import *
from tortoise.fields import ForeignKeyField as TortoiseForeignKeyField
from tortoise.fields import ManyToManyField as TortoiseManyToManyField
from tortoise.fields import OneToOneField as TortoiseOneToOneField

if TYPE_CHECKING:
    from tortoise.fields.relational import RelationalField, MODEL

# Tortoise's "model_name" argument only supports strings in the form "app.Model"
# However, Arke extensions are made of one app, and will probably never relate to models
# from other apps, therefore we make it easier by allowing Model types instead of strings


class _FakeModelNameProxy:
    def __init__(self, model: Type[models.Model]):
        self.model = model
        self.string = "."

    def __getattr__(self, __name: str) -> Any:
        return getattr(self.string, __name)

    def split(self, *args, **kwargs):
        self.string = self.model._meta.full_name
        return self.string.split(*args, **kwargs)


def _fake_related_field(related_field, model: Union[Type[models.Model], str], *args, **kwargs):
    """
    Add support for using the type class instead of a string to describe the model of a
    relational field.

    Example: ``fields.ForeignKey(MyOtherModel, on_delete=...)`` instead of Tortoise's way
    ``fields.ForeignKey("app.MyOtherModel", on_delete=...)``
    """
    if type(model) is models.ModelMeta:
        field = related_field(_FakeModelNameProxy(model), *args, **kwargs)
        return field
    return related_field(model, *args, **kwargs)


def OneToOneField(
    model: Union[Type[models.Model], str],
    related_name: Union[Optional[str], Literal[False]] = None,
    on_delete: str = CASCADE,
    db_constraint: bool = True,
    **kwargs: Any,
) -> "OneToOneRelation[MODEL]":
    return _fake_related_field(
        TortoiseOneToOneField, model, related_name, on_delete, db_constraint, **kwargs
    )


def ForeignKeyField(
    model: Union[Type[models.Model], str],
    related_name: Union[Optional[str], Literal[False]] = None,
    on_delete: str = CASCADE,
    db_constraint: bool = True,
    **kwargs: Any,
) -> "ForeignKeyRelation[MODEL]":
    return _fake_related_field(
        TortoiseForeignKeyField, model, related_name, on_delete, db_constraint, **kwargs
    )


def ManyToManyField(
    model: Union[Type[models.Model], str],
    through: Optional[str] = None,
    forward_key: Optional[str] = None,
    backward_key: str = "",
    related_name: str = "",
    on_delete: str = CASCADE,
    db_constraint: bool = True,
    **kwargs: Any,
) -> "ManyToManyRelation[MODEL]":
    return _fake_related_field(
        TortoiseManyToManyField,
        model,
        through,
        forward_key,
        backward_key,
        related_name,
        on_delete,
        db_constraint,
        **kwargs,
    )
