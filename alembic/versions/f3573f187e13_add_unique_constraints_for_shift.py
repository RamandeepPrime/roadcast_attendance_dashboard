"""Add unique constraints for shift

Revision ID: f3573f187e13
Revises: bdaff9426546
Create Date: 2024-12-26 22:08:19.925366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3573f187e13'
down_revision: Union[str, None] = 'bdaff9426546'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_unique_constraint(
        'unique_shifts_constraint', 'shifts', ['day', 'start_time', 'end_time']
    )

def downgrade() -> None:
    op.drop_constraint('unique_shifts_constraint', 'shifts', type_='unique')
