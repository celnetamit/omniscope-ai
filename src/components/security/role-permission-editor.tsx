"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Shield, Save, Plus, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface Permission {
  id: string;
  name: string;
  description: string;
  category: string;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  user_count: number;
}

export function RolePermissionEditor() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchRolesAndPermissions();
  }, []);

  const fetchRolesAndPermissions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      
      const [rolesRes, permsRes] = await Promise.all([
        fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/security/roles`,
          { headers: { Authorization: `Bearer ${token}` } }
        ),
        fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/security/permissions`,
          { headers: { Authorization: `Bearer ${token}` } }
        ),
      ]);

      if (rolesRes.ok && permsRes.ok) {
        const rolesData = await rolesRes.json();
        const permsData = await permsRes.json();
        setRoles(rolesData);
        setPermissions(permsData);
        if (rolesData.length > 0) {
          setSelectedRole(rolesData[0]);
        }
      } else {
        toast.error("Failed to load roles and permissions");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Failed to load roles and permissions");
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePermission = (permissionId: string) => {
    if (!selectedRole) return;

    const hasPermission = selectedRole.permissions.includes(permissionId);
    const updatedPermissions = hasPermission
      ? selectedRole.permissions.filter((p) => p !== permissionId)
      : [...selectedRole.permissions, permissionId];

    setSelectedRole({
      ...selectedRole,
      permissions: updatedPermissions,
    });
  };

  const handleSaveRole = async () => {
    if (!selectedRole) return;

    setSaving(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/security/roles/${selectedRole.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            permissions: selectedRole.permissions,
          }),
        }
      );

      if (response.ok) {
        toast.success("Role permissions updated");
        fetchRolesAndPermissions();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to update role");
      }
    } catch (error) {
      console.error("Save error:", error);
      toast.error("Failed to update role");
    } finally {
      setSaving(false);
    }
  };

  const permissionsByCategory = permissions.reduce((acc, perm) => {
    if (!acc[perm.category]) {
      acc[perm.category] = [];
    }
    acc[perm.category].push(perm);
    return acc;
  }, {} as Record<string, Permission[]>);

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-4">
      {/* Roles List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Roles</CardTitle>
          <CardDescription>Select a role to edit</CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[500px]">
            <div className="space-y-2">
              {roles.map((role) => (
                <div
                  key={role.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedRole?.id === role.id
                      ? "border-primary bg-primary/5"
                      : "hover:border-primary/50"
                  }`}
                  onClick={() => setSelectedRole(role)}
                >
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-medium capitalize">{role.name}</h4>
                    <Badge variant="secondary">{role.user_count}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{role.description}</p>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Permissions Editor */}
      <Card className="col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                {selectedRole ? `Edit ${selectedRole.name} Permissions` : "Select a Role"}
              </CardTitle>
              <CardDescription>
                {selectedRole
                  ? `Configure permissions for the ${selectedRole.name} role`
                  : "Choose a role from the list to edit its permissions"}
              </CardDescription>
            </div>
            {selectedRole && (
              <Button onClick={handleSaveRole} disabled={saving}>
                {saving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save
                  </>
                )}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {selectedRole ? (
            <ScrollArea className="h-[500px]">
              <div className="space-y-6 pr-4">
                {Object.entries(permissionsByCategory).map(([category, perms]) => (
                  <div key={category}>
                    <h4 className="font-medium mb-3 capitalize">{category}</h4>
                    <div className="space-y-3">
                      {perms.map((permission) => (
                        <div
                          key={permission.id}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div className="flex-1">
                            <Label
                              htmlFor={permission.id}
                              className="font-medium cursor-pointer"
                            >
                              {permission.name}
                            </Label>
                            <p className="text-sm text-muted-foreground mt-1">
                              {permission.description}
                            </p>
                          </div>
                          <Switch
                            id={permission.id}
                            checked={selectedRole.permissions.includes(permission.id)}
                            onCheckedChange={() => handleTogglePermission(permission.id)}
                          />
                        </div>
                      ))}
                    </div>
                    <Separator className="mt-6" />
                  </div>
                ))}
              </div>
            </ScrollArea>
          ) : (
            <div className="flex items-center justify-center h-[500px] text-muted-foreground">
              Select a role to edit permissions
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
