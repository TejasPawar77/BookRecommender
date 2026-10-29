from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuthorProfile, BookSummary, LibraryAccess
from .permissions import IsApprovedAuthor
from .serializers import (
    AuthorProfileSerializer,
    AuthorSummarySerializer,
    PublicSummarySerializer,
)


class PublicSummaryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicSummarySerializer

    def get_queryset(self):
        return BookSummary.objects.filter(
            status=BookSummary.Status.APPROVED,
            author__is_approved=True,
        ).select_related("author")


class PublicSummaryDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicSummarySerializer

    def get_queryset(self):
        return BookSummary.objects.filter(
            status=BookSummary.Status.APPROVED,
            author__is_approved=True,
        ).select_related("author")


class AuthorApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, "author_profile"):
            return Response(
                {"detail": "You already have an author profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AuthorProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, is_approved=False)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class AuthorSummaryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsApprovedAuthor]
    serializer_class = AuthorSummarySerializer

    def get_queryset(self):
        return BookSummary.objects.filter(
            author=self.request.user.author_profile
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user.author_profile,
            status=BookSummary.Status.PENDING,
        )


class PurchasedSummaryContentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        access = LibraryAccess.objects.filter(
            user=request.user,
            summary_id=pk,
            order_item__order__status="paid",
            order_item__order__payments__status="captured",
            order_item__order__payments__signature_verified=True,
        ).select_related("summary").first()

        if access is None:
            return Response(
                {"detail": "Purchase required to read this summary."},
                status=status.HTTP_403_FORBIDDEN,
            )

        summary = access.summary

        return Response({
            "id": summary.id,
            "book_title": summary.book_title,
            "book_author": summary.book_author,
            "full_content": summary.full_content,
        })
