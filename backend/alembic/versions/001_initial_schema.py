"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('role', sa.Enum('user', 'admin', name='userrole'), nullable=False, server_default='user'),
        sa.Column('google_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id'),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table('papers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('authors', postgresql.JSON(), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('keywords', postgresql.JSON(), nullable=True),
        sa.Column('file_url', sa.String(1000), nullable=True),
        sa.Column('file_type', sa.Enum('pdf', 'docx', 'txt', name='filetype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='paperstatus'), nullable=False, server_default='pending'),
        sa.Column('topic', sa.Enum('NLP', 'Computer Vision', 'Robotics', 'Reinforcement Learning', 'Bioinformatics', 'Healthcare AI', 'Finance AI', 'Other', name='papertopic'), nullable=False, server_default='Other'),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('parsed_sections', postgresql.JSON(), nullable=True),
        sa.Column('references', postgresql.JSON(), nullable=True),
        sa.Column('figures', postgresql.JSON(), nullable=True),
        sa.Column('tables', postgresql.JSON(), nullable=True),
        sa.Column('equations', postgresql.JSON(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('word_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_papers_user_id', 'papers', ['user_id'])
    op.create_index('ix_papers_status', 'papers', ['status'])
    op.create_index('ix_papers_topic', 'papers', ['topic'])
    op.create_index('ix_papers_created_at', 'papers', ['created_at'])

    op.create_table('authors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('affiliation', sa.String(500), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_authors_paper_id', 'authors', ['paper_id'])

    op.create_table('embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_type', sa.Enum('full_paper', 'section', 'paragraph', 'table', 'figure_caption', name='chunktype'), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('section_name', sa.String(255), nullable=True),
        sa.Column('embedding_model', sa.String(100), nullable=False),
        sa.Column('faiss_index_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_embeddings_paper_id', 'embeddings', ['paper_id'])

    op.create_table('chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=True, server_default='New Chat'),
        sa.Column('paper_ids', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'])

    op.create_table('chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('citations', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])

    op.create_table('research_ideas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_ids', postgresql.JSON(), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.Enum('easy', 'medium', 'hard', name='difficulty'), nullable=False, server_default='medium'),
        sa.Column('novelty_score', sa.Float(), nullable=True, server_default='0'),
        sa.Column('related_papers', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('knowledge_graphs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_ids', postgresql.JSON(), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('nodes', postgresql.JSON(), nullable=True),
        sa.Column('edges', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('flashcards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('front', sa.Text(), nullable=False),
        sa.Column('back', sa.Text(), nullable=False),
        sa.Column('card_type', sa.Enum('qa', 'revision', 'exam', name='cardtype'), nullable=False, server_default='qa'),
        sa.Column('difficulty', sa.Enum('easy', 'medium', 'hard', name='carddifficulty'), nullable=False, server_default='medium'),
        sa.Column('topic', sa.String(255), nullable=True),
        sa.Column('is_learned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('literature_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('topic', sa.String(500), nullable=False),
        sa.Column('paper_ids', postgresql.JSON(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('themes', postgresql.JSON(), nullable=True),
        sa.Column('trends', postgresql.JSON(), nullable=True),
        sa.Column('key_papers', postgresql.JSON(), nullable=True),
        sa.Column('gaps', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_ids', postgresql.JSON(), nullable=True),
        sa.Column('report_type', sa.String(100), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('comparison_table', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('presentations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_ids', postgresql.JSON(), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('slide_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('file_url', sa.String(1000), nullable=True),
        sa.Column('slides_data', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_analytics_user_id', 'analytics', ['user_id'])
    op.create_index('ix_analytics_event_type', 'analytics', ['event_type'])


def downgrade() -> None:
    op.drop_table('analytics')
    op.drop_table('presentations')
    op.drop_table('reports')
    op.drop_table('literature_reviews')
    op.drop_table('flashcards')
    op.drop_table('knowledge_graphs')
    op.drop_table('research_ideas')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('embeddings')
    op.drop_table('authors')
    op.drop_table('papers')
    op.drop_table('users')
