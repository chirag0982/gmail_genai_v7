from datetime import datetime
import enum
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
import uuid

# Enums for various model fields
class EmailStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    FAILED = "failed"

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager" 
    USER = "user"
    VIEWER = "viewer"

class AIModel(enum.Enum):
    QWEN_4_TURBO = "qwen-4-turbo"
    CLAUDE_4_SONNET = "claude-4-sonnet"
    GPT_4O = "gpt-4o"

class EmailTone(enum.Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CASUAL = "casual"
    URGENT = "urgent"

# User model - supports both local and OAuth authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    password_hash = db.Column(db.String, nullable=True)  # For local authentication
    
    # Email settings
    smtp_server = db.Column(db.String, nullable=True)
    smtp_port = db.Column(db.Integer, nullable=True)
    smtp_username = db.Column(db.String, nullable=True)
    smtp_password = db.Column(db.String, nullable=True)  # Encrypted
    smtp_use_tls = db.Column(db.Boolean, default=True)
    
    # AI preferences
    preferred_ai_model = db.Column(db.Enum(AIModel), default=AIModel.QWEN_4_TURBO)
    default_tone = db.Column(db.Enum(EmailTone), default=EmailTone.PROFESSIONAL)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    team_memberships = db.relationship('TeamMember', back_populates='user', cascade='all, delete-orphan')
    emails = db.relationship('Email', back_populates='user', cascade='all, delete-orphan')
    templates = db.relationship('EmailTemplate', back_populates='user', cascade='all, delete-orphan')

# OAuth model - mandatory for Replit Auth
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

# Team model
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Team settings
    ai_model_access = db.Column(db.JSON, default=lambda: ["qwen-4-turbo", "claude-4-sonnet", "gpt-4o"])
    monthly_token_limit = db.Column(db.Integer, default=100000)
    require_approval = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    members = db.relationship('TeamMember', back_populates='team', cascade='all, delete-orphan')
    emails = db.relationship('Email', back_populates='team', cascade='all, delete-orphan')
    templates = db.relationship('EmailTemplate', back_populates='team', cascade='all, delete-orphan')

# Team invitations model
class TeamInvitation(db.Model):
    __tablename__ = 'team_invitations'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=False)
    invited_user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    invited_by_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    
    # Invitation status
    status = db.Column(db.String, default='pending')  # pending, accepted, declined
    message = db.Column(db.Text)  # Optional invitation message
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    responded_at = db.Column(db.DateTime)
    
    # Relationships
    team = db.relationship('Team', foreign_keys=[team_id])
    invited_user = db.relationship('User', foreign_keys=[invited_user_id])
    invited_by = db.relationship('User', foreign_keys=[invited_by_id])
    
    __table_args__ = (UniqueConstraint('team_id', 'invited_user_id', name='uq_team_invitation'),)

# Team membership model
class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    
    joined_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    user = db.relationship('User', back_populates='team_memberships')
    team = db.relationship('Team', back_populates='members')
    
    __table_args__ = (UniqueConstraint('user_id', 'team_id', name='uq_user_team'),)

# Email model
class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=True)
    
    # Email content
    subject = db.Column(db.String(255), nullable=False)
    body_html = db.Column(db.Text)
    body_text = db.Column(db.Text)
    
    # Recipients
    to_addresses = db.Column(db.JSON)  # List of email addresses
    cc_addresses = db.Column(db.JSON)  # List of email addresses
    bcc_addresses = db.Column(db.JSON)  # List of email addresses
    
    # Email metadata
    status = db.Column(db.Enum(EmailStatus), default=EmailStatus.DRAFT)
    ai_model_used = db.Column(db.Enum(AIModel))
    tone_used = db.Column(db.Enum(EmailTone))
    original_email = db.Column(db.Text)  # The email being replied to
    context = db.Column(db.Text)  # Additional context provided
    
    # Analytics
    generation_time_ms = db.Column(db.Integer)
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    replied_at = db.Column(db.DateTime)
    user_rating = db.Column(db.Integer)  # 1-5 rating
    edited_before_send = db.Column(db.Boolean, default=False)
    
    # Scheduling
    scheduled_send_time = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = db.relationship('User', back_populates='emails')
    team = db.relationship('Team', back_populates='emails')
    drafts = db.relationship('EmailDraft', back_populates='email', cascade='all, delete-orphan')

# Email drafts for collaboration
class EmailDraft(db.Model):
    __tablename__ = 'email_drafts'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email_id = db.Column(db.String, db.ForeignKey('emails.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    email = db.relationship('Email', back_populates='drafts')

# Email templates
class EmailTemplate(db.Model):
    __tablename__ = 'email_templates'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=True)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_template = db.Column(db.String(255))
    body_template = db.Column(db.Text)
    
    # Template settings
    default_tone = db.Column(db.Enum(EmailTone))
    is_public = db.Column(db.Boolean, default=False)  # Visible to team
    
    usage_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = db.relationship('User', back_populates='templates')
    team = db.relationship('Team', back_populates='templates')

# Analytics model
class EmailAnalytics(db.Model):
    __tablename__ = 'email_analytics'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=False)
    email_id = db.Column(db.String, db.ForeignKey('emails.id'), nullable=False)
    
    # Tracking data
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    replied_at = db.Column(db.DateTime)
    
    # AI metrics
    ai_model_used = db.Column(db.String(50))
    generation_time_ms = db.Column(db.Integer)
    user_rating = db.Column(db.Integer)
    edited_before_send = db.Column(db.Boolean, default=False)
    edit_percentage = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.now)

# Collaboration sessions for real-time editing
class CollaborationSession(db.Model):
    __tablename__ = 'collaboration_sessions'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email_id = db.Column(db.String, db.ForeignKey('emails.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.now)
    cursor_position = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.now)

# Token usage tracking per team member
class TokenUsage(db.Model):
    __tablename__ = 'token_usage'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=False)
    
    # Usage details
    ai_model = db.Column(db.String(50), nullable=False)  # Which model was used
    operation_type = db.Column(db.String(30), nullable=False)  # 'email_generation', 'analysis', 'summarization'
    tokens_consumed = db.Column(db.Integer, nullable=False)
    cost_usd = db.Column(db.Float, default=0.0)
    
    # Performance metrics
    generation_time_ms = db.Column(db.Integer)
    quality_score = db.Column(db.Float)  # AI-assessed quality (1-10)
    user_satisfaction = db.Column(db.Integer)  # User rating 1-5 stars
    
    # Context
    email_id = db.Column(db.String, db.ForeignKey('emails.id'), nullable=True)
    prompt_length = db.Column(db.Integer)
    response_length = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    user = db.relationship('User')
    team = db.relationship('Team')
    email = db.relationship('Email')

# AI-powered team insights and recommendations  
class TeamAIInsights(db.Model):
    __tablename__ = 'team_ai_insights'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=False)
    
    # Insight types: 'productivity', 'collaboration', 'cost_optimization', 'quality'
    insight_type = db.Column(db.String(30), nullable=False)
    insight_title = db.Column(db.String(200), nullable=False)
    insight_description = db.Column(db.Text, nullable=False)
    
    # AI recommendations
    recommendation = db.Column(db.Text)
    confidence_score = db.Column(db.Float, default=0.0)  # 0-1 confidence
    priority_level = db.Column(db.String(10), default='medium')  # low, medium, high
    
    # Tracking
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    data_points_analyzed = db.Column(db.Integer, default=0)
    generated_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime, nullable=True)  # Some insights expire
    
    # Relationships
    team = db.relationship('Team')
    acknowledged_by = db.relationship('User')

# Team collaboration patterns and AI coaching
class TeamCollaborationPattern(db.Model):
    __tablename__ = 'team_collaboration_patterns'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=False)
    
    # Pattern analysis
    pattern_name = db.Column(db.String(100), nullable=False)
    pattern_description = db.Column(db.Text)
    frequency_score = db.Column(db.Float, default=0.0)  # How often this pattern occurs
    
    # AI coaching suggestions
    ai_coaching_tip = db.Column(db.Text)
    improvement_potential = db.Column(db.String(20))  # 'low', 'medium', 'high'
    
    # Member involvement
    primary_participants = db.Column(db.JSON)  # List of user IDs most involved
    collaboration_quality = db.Column(db.Float, default=0.0)  # 1-10 scale
    
    # Time tracking
    first_observed = db.Column(db.DateTime, default=datetime.now)
    last_observed = db.Column(db.DateTime, default=datetime.now)
    analysis_period_days = db.Column(db.Integer, default=7)
    
    # Relationships  
    team = db.relationship('Team')

# Smart email suggestions and auto-responses
class SmartEmailSuggestion(db.Model):
    __tablename__ = 'smart_email_suggestions'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = db.Column(db.String, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    # Suggestion context
    trigger_email_content = db.Column(db.Text)  # Original email that triggered suggestion
    suggestion_type = db.Column(db.String(30))  # 'quick_reply', 'template', 'tone_adjustment'
    suggested_content = db.Column(db.Text, nullable=False)
    
    # AI analysis
    relevance_score = db.Column(db.Float, default=0.0)  # How relevant (0-1)
    tone_match_score = db.Column(db.Float, default=0.0)  # How well it matches user's style
    predicted_effectiveness = db.Column(db.Float, default=0.0)  # Predicted success rate
    
    # User interaction
    was_used = db.Column(db.Boolean, default=False)
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars if used
    modified_before_use = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    team = db.relationship('Team')
    user = db.relationship('User')
