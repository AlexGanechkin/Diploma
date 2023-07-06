""" Пакет сериализаторов для создания/просмотра/изменения/удаления сущностей приложения

Данный модуль описывает сериализаторы для:
- досок:
    BoardSerializer - для создания доски;
    BoardParticipantSerializer - для получения участника доски;
    BoardWithParticipantSerializer - для получения детальной информации по доске, обновление списка участников доски;
- категорий:
    GoalCategorySerializer - для создания категории;
    GoalCategoryWithUserSerializer - для получения списка категорий и детальной информации по категории;
- целей:
    GoalSerializer - для создания цели;
    GoalWithUserSerializer - для получения списка целей и детальной информации по цели;
- комментариев:
    GoalCommentSerializer - для создания комментария;
    GoalCommentWithUserSerializer - для получения списка комментариев и детальной информации по комментарию

"""

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.request import Request

from core.models import User
from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.editable_roles)
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')

    def validate_user(self, user: User) -> User:
        """ Проверяет роль пользователя """

        if self.context['request'].user == user:
            raise ValidationError('Failed to change your role')
        return user


class BoardWithParticipantSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(many=True)

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def update(self, instance: Board, validated_data: dict) -> Board:
        """ Обновляет список участников доски, обновляет название доски """

        request: Request = self.context['request']

        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=request.user).delete()
            BoardParticipant.objects.bulk_create(
                [
                    BoardParticipant(user=participant['user'], role=participant['role'], board=instance)
                    for participant in validated_data.get('participants', [])
                ],
                ignore_conflicts=True,
            )

            if title := validated_data.get('title'):
                instance.title = title

            instance.save()

        return instance


class GoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')

    def validate_board(self, board: Board) -> Board:
        """ Проверяет наличие доски у категории, права пользователя на доступ к категории """

        if board.is_deleted:
            raise ValidationError('Board is deleted')

        if not BoardParticipant.objects.filter(
                    board_id=board.id,
                    role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                    user_id=self.context['request'].user
                ).exists():
            raise PermissionDenied

        return board


class GoalCategoryWithUserSerializer(GoalCategorySerializer):
    user = UserSerializer(read_only=True)


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        """ Проверяет наличие категории, права пользователя на создание цели """

        if value.is_deleted:
            raise ValidationError('Category not found')

        if not BoardParticipant.objects.filter(
                board_id=value.board.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user
        ).exists():
            raise PermissionDenied('must be owner or writer in project')

        return value

    def validate_created(self):
        pass


class GoalWithUserSerializer(GoalSerializer):
    user = UserSerializer(read_only=True)


class GoalCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')

    def validate_goal(self, value):
        """ Проверяет наличие цели, права пользователя на создание/редактирование комментария """

        if value.status == Goal.Status.archived:
            raise ValidationError('Goal not found')

        if not BoardParticipant.objects.filter(
                    board_id=value.category.board.id,
                    role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                    user_id=self.context['request'].user
                ).exists():
            raise PermissionDenied

        return value


class GoalCommentWithUserSerializer(GoalCommentSerializer):
    user = UserSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)
