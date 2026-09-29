"""add cascade deletes

Revision ID: 25db45b0714a
Revises: e1345abf9c1e
Create Date: 2026-09-29 15:19:53.789255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25db45b0714a'
down_revision: Union[str, Sequence[str], None] = 'e1345abf9c1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("experiments_project_id_fkey"),
        "experiments",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_experiments_project_id_projects",
        "experiments",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        op.f("runs_experiment_id_fkey"),
        "runs",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_runs_experiment_id_experiments",
        "runs",
        "experiments",
        ["experiment_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_runs_experiment_id_experiments",
        "runs",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("runs_experiment_id_fkey"),
        "runs",
        "experiments",
        ["experiment_id"],
        ["id"],
    )

    op.drop_constraint(
        "fk_experiments_project_id_projects",
        "experiments",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("experiments_project_id_fkey"),
        "experiments",
        "projects",
        ["project_id"],
        ["id"],
    )
