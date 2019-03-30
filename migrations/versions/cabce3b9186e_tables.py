"""tables

Revision ID: cabce3b9186e
Revises: 9f027a43b094
Create Date: 2019-03-10 22:57:26.173568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cabce3b9186e'
down_revision = '9f027a43b094'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('game_mode', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('summoner',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('indexed_name', sa.String(length=32), nullable=True),
    sa.Column('level', sa.String(length=50), nullable=True),
    sa.Column('profile_icon', sa.String(length=50), nullable=True),
    sa.Column('account_id', sa.String(length=128), nullable=True),
    sa.Column('summoner_id', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('account_id'),
    sa.UniqueConstraint('indexed_name'),
    sa.UniqueConstraint('summoner_id')
    )
    op.create_index(op.f('ix_summoner_name'), 'summoner', ['name'], unique=True)
    op.create_table('match_by_reference',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('summoner_id', sa.Integer(), nullable=True),
    sa.Column('lane_played', sa.String(length=20), nullable=True),
    sa.Column('champion_played', sa.String(length=20), nullable=True),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('game_mode', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['summoner_id'], ['summoner.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('indexed_name', sa.String(length=32), nullable=True),
    sa.Column('champion_played', sa.String(length=20), nullable=True),
    sa.Column('champion_level', sa.Integer(), nullable=True),
    sa.Column('win', sa.Integer(), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('participant_id', sa.Integer(), nullable=True),
    sa.Column('spell1', sa.Integer(), nullable=True),
    sa.Column('spell2', sa.Integer(), nullable=True),
    sa.Column('item1', sa.Integer(), nullable=True),
    sa.Column('item2', sa.Integer(), nullable=True),
    sa.Column('item3', sa.Integer(), nullable=True),
    sa.Column('item4', sa.Integer(), nullable=True),
    sa.Column('item5', sa.Integer(), nullable=True),
    sa.Column('item6', sa.Integer(), nullable=True),
    sa.Column('item7', sa.Integer(), nullable=True),
    sa.Column('kills', sa.Integer(), nullable=True),
    sa.Column('deaths', sa.Integer(), nullable=True),
    sa.Column('assists', sa.Integer(), nullable=True),
    sa.Column('damage_dealt', sa.Integer(), nullable=True),
    sa.Column('damage_healed', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('player')
    op.drop_table('match_by_reference')
    op.drop_index(op.f('ix_summoner_name'), table_name='summoner')
    op.drop_table('summoner')
    op.drop_table('match')
    # ### end Alembic commands ###
