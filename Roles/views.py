from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Role, Permission
from .serializers import RoleSerializer, PermissionSerializer


class RolesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            data = request.GET
            count = int(data.get("count", 0))
            page = int(data.get("page", 0))
            search = data.get("search")

            offset = count * page if count else 0

            roles = Role.objects.filter(active=True).order_by("-updated_at")
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

    def post(self, request):
        try:
            serializer = RoleSerializer(data=request.data)
            if serializer.is_valid():
                role = serializer.save()
                return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, name=None):
        role = get_object_or_404(Role, name=name)
        serializer = RoleSerializer(role, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, name=None):
        role = get_object_or_404(Role, name=name)
        role.active = False
        role.save()
        return Response({"details": "Role deleted successfully"}, status=status.HTTP_200_OK)


class PermissionsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            data = request.GET
            count = int(data.get("count", 0))
            page = int(data.get("page", 0))
            search = data.get("search")

            offset = count * page if count else 0

            permissions = Permission.objects.filter(active=True).order_by("-updated_at")
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

    def post(self, request):
        try:
            serializer = PermissionSerializer(data=request.data)
            if serializer.is_valid():
                permission = serializer.save()  
                return Response(PermissionSerializer(permission).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, code=None):
        permission = get_object_or_404(Permission, code=code)
        serializer = PermissionSerializer(permission, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code=None):
        permission = get_object_or_404(Permission, code=code)
        permission.active = False
        permission.save()
        return Response({"details": "Permission deleted successfully"}, status=status.HTTP_200_OK)
