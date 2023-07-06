""" Набор представлений для управления целями (CRUD)

GoalCreateView - создание цели (любой аутентифицированный пользователь)
GoalListView - формирование списка целей (доступно любому участнику доски)
GoalDetailView - предоставление информации по отдельной цели / ее изменение / удаление
(при удалении цели помечаются в БД как архивные)

"""
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, filters
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView

from goals.filters import GoalFilter
from goals.models import Goal
from goals.permissions import GoalPermission
from goals.serializers import GoalSerializer, GoalWithUserSerializer


class GoalCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer


class GoalListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalWithUserSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalFilter
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self) -> QuerySet[Goal]:
        """ Показывает участникам цели за исключением архивных """

        return Goal.objects.filter(
                category__board__participants__user=self.request.user,
            ).exclude(status=Goal.Status.archived)

    # def get_queryset(self): предыдущая версия
    #     return Goal.objects.select_related('user').filter(
    #         user=self.request.user, category__is_deleted=False
    #     ).exclude(status=Goal.Status.archived)


class GoalDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalPermission]
    serializer_class = GoalWithUserSerializer
    queryset = Goal.objects.exclude(status=Goal.Status.archived)

    def perform_destroy(self, instance: Goal) -> None:
        """ При удалении цели присваивает ей статус архивная """

        instance.status = Goal.Status.archived
        instance.save(update_fields=['status'])
