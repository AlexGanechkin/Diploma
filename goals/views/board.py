""" Набор представлений для управления досками (CRUD)

BoardCreateView - создание доски (любой аутентифицированный пользователь)
BoardListView - формирование списка досок (доступно участнику: владельцу/редактору/читателю)
BoardDetailView - предоставление информации по отдельной доске / ее изменение / удаление (доступно только владельцу)
(при удалении доски остаются в БД со статусом удалена)

"""

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import generics, filters, permissions

from goals.models import BoardParticipant, Board, Goal
from goals.permissions import BoardPermission
from goals.serializers import BoardSerializer, BoardWithParticipantSerializer


class BoardCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer

    def perform_create(self, serializer: BoardSerializer) -> None:
        """ Создает доску и присваивает создавшему пользователю роль владельца """

        with transaction.atomic():
            board = serializer.save()
            BoardParticipant.objects.create(user=self.request.user, board=board, role=BoardParticipant.Role.owner)


class BoardListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self) -> QuerySet[Board]:
        """ Показывает доски участникам за исключением удаленных """

        return Board.objects.filter(participants__user=self.request.user).exclude(is_deleted=True)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [BoardPermission]
    serializer_class = BoardWithParticipantSerializer
    queryset = Board.objects.prefetch_related('participants__user').exclude(is_deleted=True)

    def perform_destroy(self, instance: Board) -> None:
        """ При удалении доски также удаляет категории / архивирует цели, связанные с ней """

        with transaction.atomic():
            Board.objects.filter(id=instance.id).update(is_deleted=True)
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
