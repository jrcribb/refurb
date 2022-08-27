from dataclasses import dataclass

from mypy.nodes import CallExpr, NameExpr, OpExpr

from refurb.error import Error


@dataclass
class ErrorUseIsinstanceTuple(Error):
    """
    `isinstance()` and `issubclass()` both take tuple arguments, so instead of
    calling them multiple times for the same object, you can check all of them
    at once:

    Bad:

    ```
    if isinstance(num, float) or isinstance(num, int):
        pass
    ```

    Good:

    ```
    if isinstance(num, (float, int)):
        pass
    ```

    Note: In python 3.10+ you can also pass type unions as the second param to
    these functions:

    ```
    if isinstance(num, float | int):
        pass
    ```
    """

    code = 121


def check(node: OpExpr, errors: list[Error]) -> None:
    match node:
        case OpExpr(
            op="or",
            left=CallExpr(callee=NameExpr() as lhs, args=lhs_args),
            right=CallExpr(callee=NameExpr() as rhs, args=rhs_args),
        ) if (
            lhs.fullname == rhs.fullname
            and lhs.fullname in ("builtins.isinstance", "builtins.issubclass")
            and len(lhs_args) == 2
            and str(lhs_args[0]) == str(rhs_args[0])
        ):
            errors.append(
                ErrorUseIsinstanceTuple(
                    lhs_args[1].line,
                    lhs_args[1].column,
                    msg=f"Replace `{lhs.name}(x, y) or {lhs.name}(x, z)` with `{lhs.name}(x, (y, z))`",  # noqa: E501
                )
            )