import pytest

from protox.plugin.common import to_snake_case


@pytest.mark.parametrize(
    'name, snake_case_name',
    [
        ('A', 'a'),
        ('a', 'a'),
        ('SnakeCaseName', 'snake_case_name'),
        ('hello_world', 'hello_world'),
    ],
)
def test_to_snake_case(name, snake_case_name):
    assert to_snake_case(name) == snake_case_name
