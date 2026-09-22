import json

from sqlmodel import Session, select

from app.content.admin_directories import ADMIN_DIRECTORIES
from app.content.alerting_escalation import ALERTING_ESCALATION
from app.content.application_backup_strategy import APPLICATION_BACKUP_STRATEGY
from app.content.application_dns import APPLICATION_DNS
from app.content.application_health_checks import APPLICATION_HEALTH_CHECKS
from app.content.application_monitoring import APPLICATION_MONITORING
from app.content.basic_system_diagnostics import BASIC_SYSTEM_DIAGNOSTICS
from app.content.certbot_https import CERTBOT_HTTPS
from app.content.ci_tests_build import CI_TESTS_BUILD
from app.content.compose_app_database import COMPOSE_APP_DATABASE
from app.content.container_basics import CONTAINER_BASICS
from app.content.container_data_network import CONTAINER_DATA_NETWORK
from app.content.container_lifecycle import CONTAINER_LIFECYCLE
from app.content.deployment_backup_rollback import DEPLOYMENT_BACKUP_ROLLBACK
from app.content.deployment_checklist import DEPLOYMENT_CHECKLIST
from app.content.deployment_preparation import DEPLOYMENT_PREPARATION
from app.content.disk_space_cleanup import DISK_SPACE_CLEANUP
from app.content.dns_practice import DNS_PRACTICE
from app.content.docker_build_cache import DOCKER_BUILD_CACHE
from app.content.dockerfile_web_app import DOCKERFILE_WEB_APP
from app.content.environment_secrets import ENVIRONMENT_SECRETS
from app.content.file_permissions import FILE_PERMISSIONS
from app.content.files_and_directories import FILES_AND_DIRECTORIES
from app.content.firewall_basics import FIREWALL_BASICS
from app.content.firewalld_zones_services_ports import FIREWALLD_ZONES_SERVICES_PORTS
from app.content.git_application_update import GIT_APPLICATION_UPDATE
from app.content.github_actions_first_workflow import GITHUB_ACTIONS_FIRST_WORKFLOW
from app.content.incident_diagnosis_workflow import INCIDENT_DIAGNOSIS_WORKFLOW
from app.content.ip_addressing import IP_ADDRESSING
from app.content.log_analysis import LOG_ANALYSIS
from app.content.metrics_percentiles import METRICS_PERCENTILES
from app.content.network_diagnostics import NETWORK_DIAGNOSTICS
from app.content.network_dns_routing_connections import NETWORK_DNS_ROUTING_CONNECTIONS
from app.content.network_ports_services import NETWORK_PORTS_SERVICES
from app.content.nginx_reverse_proxy import NGINX_REVERSE_PROXY
from app.content.observability_signals import OBSERVABILITY_SIGNALS
from app.content.operations_runbook import OPERATIONS_RUNBOOK
from app.content.package_management import PACKAGE_MANAGEMENT
from app.content.pipeline_delivery_diagnostics import PIPELINE_DELIVERY_DIAGNOSTICS
from app.content.post_deployment_diagnostics import POST_DEPLOYMENT_DIAGNOSTICS
from app.content.postgres_backup_container import POSTGRES_BACKUP_CONTAINER
from app.content.postgres_container import POSTGRES_CONTAINER
from app.content.postgres_persistence import POSTGRES_PERSISTENCE
from app.content.postgres_restore_test import POSTGRES_RESTORE_TEST
from app.content.processes import PROCESSES
from app.content.python_server_environment import PYTHON_SERVER_ENVIRONMENT
from app.content.scheduled_tasks import SCHEDULED_TASKS
from app.content.secure_container_image import SECURE_CONTAINER_IMAGE
from app.content.selinux_basics import SELINUX_BASICS
from app.content.selinux_troubleshooting import SELINUX_TROUBLESHOOTING
from app.content.service_application_logs import SERVICE_APPLICATION_LOGS
from app.content.service_objectives import SERVICE_OBJECTIVES
from app.content.ssh_administration import SSH_ADMINISTRATION
from app.content.ssh_keys_practice import SSH_KEYS_PRACTICE
from app.content.ssh_secure_configuration import SSH_SECURE_CONFIGURATION
from app.content.sudo_administration import SUDO_ADMINISTRATION
from app.content.system_logs import SYSTEM_LOGS
from app.content.system_services import SYSTEM_SERVICES
from app.content.systemd_diagnostics import SYSTEMD_DIAGNOSTICS
from app.content.systemd_web_service import SYSTEMD_WEB_SERVICE
from app.content.terminal_navigation import TERMINAL_NAVIGATION
from app.content.text_files import TEXT_FILES
from app.content.tls_https_basics import TLS_HTTPS_BASICS
from app.content.user_management import USER_MANAGEMENT
from app.content.users_and_groups import USERS_AND_GROUPS
from app.content.uvicorn_application import UVICORN_APPLICATION
from app.database import engine
from app.models import Flashcard, LearningModule, Lesson, Quiz, QuizAnswer, QuizQuestion

LESSONS = [
    TERMINAL_NAVIGATION,
    FILES_AND_DIRECTORIES,
    FILE_PERMISSIONS,
    USERS_AND_GROUPS,
    PROCESSES,
    TEXT_FILES,
    PACKAGE_MANAGEMENT,
    SYSTEM_SERVICES,
    NETWORK_DIAGNOSTICS,
    SYSTEM_LOGS,
    ADMIN_DIRECTORIES,
    BASIC_SYSTEM_DIAGNOSTICS,
    SUDO_ADMINISTRATION,
    USER_MANAGEMENT,
    SYSTEMD_DIAGNOSTICS,
    LOG_ANALYSIS,
    DISK_SPACE_CLEANUP,
    SCHEDULED_TASKS,
    IP_ADDRESSING,
    DNS_PRACTICE,
    NETWORK_PORTS_SERVICES,
    SSH_ADMINISTRATION,
    FIREWALL_BASICS,
    SELINUX_BASICS,
    SSH_SECURE_CONFIGURATION,
    SSH_KEYS_PRACTICE,
    FIREWALLD_ZONES_SERVICES_PORTS,
    SELINUX_TROUBLESHOOTING,
    NETWORK_DNS_ROUTING_CONNECTIONS,
    TLS_HTTPS_BASICS,
    DEPLOYMENT_PREPARATION,
    PYTHON_SERVER_ENVIRONMENT,
    UVICORN_APPLICATION,
    SYSTEMD_WEB_SERVICE,
    NGINX_REVERSE_PROXY,
    APPLICATION_DNS,
    CERTBOT_HTTPS,
    ENVIRONMENT_SECRETS,
    GIT_APPLICATION_UPDATE,
    DEPLOYMENT_BACKUP_ROLLBACK,
    POST_DEPLOYMENT_DIAGNOSTICS,
    DEPLOYMENT_CHECKLIST,
    CONTAINER_BASICS,
    CONTAINER_LIFECYCLE,
    CONTAINER_DATA_NETWORK,
    DOCKERFILE_WEB_APP,
    DOCKER_BUILD_CACHE,
    SECURE_CONTAINER_IMAGE,
    POSTGRES_CONTAINER,
    COMPOSE_APP_DATABASE,
    POSTGRES_PERSISTENCE,
    GITHUB_ACTIONS_FIRST_WORKFLOW,
    CI_TESTS_BUILD,
    PIPELINE_DELIVERY_DIAGNOSTICS,
    APPLICATION_HEALTH_CHECKS,
    OBSERVABILITY_SIGNALS,
    SERVICE_APPLICATION_LOGS,
    APPLICATION_MONITORING,
    METRICS_PERCENTILES,
    ALERTING_ESCALATION,
    SERVICE_OBJECTIVES,
    INCIDENT_DIAGNOSIS_WORKFLOW,
    APPLICATION_BACKUP_STRATEGY,
    POSTGRES_BACKUP_CONTAINER,
    POSTGRES_RESTORE_TEST,
    OPERATIONS_RUNBOOK,
]


def sync_module(session, module_data):
    module = session.exec(
        select(LearningModule).where(LearningModule.title == module_data["title"])
    ).first()

    if not module:
        module = LearningModule(
            title=module_data["title"],
            description=module_data["description"],
        )
        session.add(module)
    else:
        module.description = module_data["description"]

    session.commit()
    session.refresh(module)

    return module


def sync_lesson(session, module, lesson_data):
    lesson = session.exec(
        select(Lesson).where(
            Lesson.module_id == module.id,
            Lesson.title == lesson_data["title"],
        )
    ).first()

    lesson_values = {
        "module_id": module.id,
        "title": lesson_data["title"],
        "level": lesson_data["level"],
        "duration": lesson_data["duration"],
        "description": lesson_data["description"],
        "theory": lesson_data["theory"],
        "commands_json": json.dumps(lesson_data["commands"], ensure_ascii=False),
        "practice_task": lesson_data["practice_task"],
        "common_mistakes_json": json.dumps(
            lesson_data["common_mistakes"],
            ensure_ascii=False,
        ),
        "summary": lesson_data["summary"],
    }

    if not lesson:
        lesson = Lesson(**lesson_values)
        session.add(lesson)
    else:
        for field, value in lesson_values.items():
            setattr(lesson, field, value)

    session.commit()
    session.refresh(lesson)

    return lesson


def delete_quiz_questions(session, quiz):
    questions = session.exec(
        select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id)
    ).all()

    for question in questions:
        answers = session.exec(
            select(QuizAnswer).where(QuizAnswer.question_id == question.id)
        ).all()

        for answer in answers:
            session.delete(answer)

        session.delete(question)

    session.commit()


def sync_quiz(session, lesson, quiz_data):
    quiz = session.exec(select(Quiz).where(Quiz.lesson_id == lesson.id)).first()

    if not quiz:
        quiz = Quiz(
            lesson_id=lesson.id,
            title=quiz_data["title"],
            description=quiz_data["description"],
        )
        session.add(quiz)
    else:
        quiz.title = quiz_data["title"]
        quiz.description = quiz_data["description"]

    session.commit()
    session.refresh(quiz)

    delete_quiz_questions(session, quiz)

    for index, question_data in enumerate(quiz_data["questions"], start=1):
        question = QuizQuestion(
            quiz_id=quiz.id,
            text=question_data["text"],
            position=index,
        )
        session.add(question)
        session.commit()
        session.refresh(question)

        for option_key, answer_text, is_correct in question_data["answers"]:
            answer = QuizAnswer(
                question_id=question.id,
                option_key=option_key,
                text=answer_text,
                is_correct=is_correct,
            )
            session.add(answer)

    session.commit()

    return quiz


def sync_flashcards(session, lesson, flashcards_data):
    existing_flashcards = session.exec(
        select(Flashcard).where(Flashcard.lesson_id == lesson.id)
    ).all()

    for flashcard in existing_flashcards:
        session.delete(flashcard)

    session.commit()

    for index, flashcard_data in enumerate(flashcards_data, start=1):
        flashcard = Flashcard(
            lesson_id=lesson.id,
            question=flashcard_data["question"],
            answer=flashcard_data["answer"],
            position=index,
        )
        session.add(flashcard)

    session.commit()


def seed_database():
    with Session(engine) as session:
        for lesson_bundle in LESSONS:
            module = sync_module(session, lesson_bundle["module"])
            lesson = sync_lesson(session, module, lesson_bundle["lesson"])

            sync_quiz(session, lesson, lesson_bundle["quiz"])
            sync_flashcards(session, lesson, lesson_bundle["flashcards"])
