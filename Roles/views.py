from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import UserRole, UserPermission
from .serializers import RoleSerializer, PermissionSerializer


class RolesView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="List all roles with optional pagination and search",
        manual_parameters=[
            openapi.Parameter("count", openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
            openapi.Parameter("page", openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter("search", openapi.IN_QUERY, description="Search by role name", type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response("Roles list", RoleSerializer(many=True))}
    )
    def get(self, request):
        try:
            data = request.GET
            count = int(data.get("count", 0))
            page = int(data.get("page", 0))
            search = data.get("search")

            offset = count * page if count else 0

            roles = UserRole.objects.filter(active=True).order_by("-updated_at")
            if search:
                roles = roles.filter(name__icontains=search)
            total_count = roles.count()

            if count:
                page_end = offset + count
                roles = roles[offset:page_end]
                if page_end > total_count:
                    page_end = total_count
            else:
                page_end = total_count

            roles = RoleSerializer(roles, many=True).data

            return Response(
                {
                    "data": roles,
                    "pageStart": offset + 1 if len(roles) else 0,
                    "pageEnd": page_end,
                    "totalCount": total_count,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new role",
        request_body=RoleSerializer,
        responses={201: RoleSerializer}
    )
    def post(self, request):
        try:
            serializer = RoleSerializer(data=request.data)
            if serializer.is_valid():
                role = serializer.save()
                permissions = request.data.get("user_permissions", [])
                if permissions:
                    role.user_permissions.set(permissions)
                return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error"  , e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a role by name",
        request_body=RoleSerializer,
        responses={200: RoleSerializer}
    )
    def put(self, request, name=None):
        role = get_object_or_404(UserRole, name=name)
        serializer = RoleSerializer(role, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Soft delete a role by name",
        responses={200: openapi.Response("Role deleted successfully")}
    )
    def delete(self, request, name=None):
        role = get_object_or_404(UserRole, name=name)
        role.active = False
        role.save()
        return Response({"details": "Role deleted successfully"}, status=status.HTTP_200_OK)


class PermissionsView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="List all permissions with optional pagination and search",
        manual_parameters=[
            openapi.Parameter("count", openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
            openapi.Parameter("page", openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter("search", openapi.IN_QUERY, description="Search by permission code", type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response("Permissions list", PermissionSerializer(many=True))}
    )
    def get(self, request):
        try:
            data = request.GET
            count = int(data.get("count", 0))
            page = int(data.get("page", 0))
            search = data.get("search")

            offset = count * page if count else 0

            permissions = UserPermission.objects.filter(active=True).order_by("-updated_at")
            if search:
                permissions = permissions.filter(code__icontains=search)
            total_count = permissions.count()

            if count:
                page_end = offset + count
                permissions = permissions[offset:page_end]
                if page_end > total_count:
                    page_end = total_count
            else:
                page_end = total_count

            permissions = PermissionSerializer(permissions, many=True).data

            return Response(
                {
                    "data": permissions,
                    "pageStart": offset + 1 if len(permissions) else 0,
                    "pageEnd": page_end,
                    "totalCount": total_count,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new permission",
        request_body=PermissionSerializer,
        responses={201: PermissionSerializer}
    )
    def post(self, request):
        try:
            serializer = PermissionSerializer(data=request.data)
            if serializer.is_valid():
                permission = serializer.save()  
                return Response(PermissionSerializer(permission).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a permission by code",
        request_body=PermissionSerializer,
        responses={200: PermissionSerializer}
    )
    def put(self, request, code=None):
        permission = get_object_or_404(UserPermission, code=code)
        serializer = PermissionSerializer(permission, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Soft delete a permission by code",
        responses={200: openapi.Response("Permission deleted successfully")}
    )
    def delete(self, request, code=None):
        permission = get_object_or_404(UserPermission, code=code)
        permission.active = False
        permission.save()
        return Response({"details": "Permission deleted successfully"}, status=status.HTTP_200_OK)
