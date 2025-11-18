declare namespace AdminService {
  // Existing types
  interface LoginData {
    access_token: string;
    token_type: string;
  }

  interface ListUsersItem {
    email: string;
    nickname: string;
    create_date: string;
    is_active: boolean;
    is_superuser: boolean;
  }

  interface UserDetail {
    email: string;
    language: string;
    last_login_time: string;
    is_active: boolean;
    is_anonymous: boolean;
    login_channel: string;
    status: string;
    is_superuser: boolean;
    create_date: string;
    update_date: string;
  }

  interface ListUserDatasetItem {
    id: string;
    name: string;
    description: string;
    create_date: string;
  }

  interface ListUserAgentItem {
    id: string;
    name: string;
    description: string;
    create_date: string;
  }

  interface ListServicesItem {
    id: number;
    name: string;
    status: string;
    type: string;
  }

  interface ServiceDetail {
    id: number;
    name: string;
    status: string;
    type: string;
    version: string;
    config: Record<string, any>;
  }

  interface ListRoleItem {
    id: string;
    role_name: string;
    description: string;
    create_date: string;
  }

  interface ListRoleItemWithPermission extends ListRoleItem {
    permissions: string[];
  }

  interface RoleDetail {
    id: string;
    role_name: string;
    description: string;
    create_date: string;
    update_date: string;
  }

  interface RoleDetailWithPermission extends RoleDetail {
    permissions: ResourcePermissions;
  }

  interface ResourcePermissions {
    [resourceName: string]: string[];
  }

  interface AssignRolePermissionsInput {
    [resourceName: string]: string[];
  }

  interface RevokeRolePermissionInput {
    [resourceName: string]: string[];
  }

  interface UserDetailWithPermission extends UserDetail {
    role: string;
    permissions: ResourcePermissions;
  }

  interface ResourceType {
    [resourceName: string]: string[];
  }

  interface ListWhitelistItem {
    id: number;
    email: string;
    create_date: string;
  }

  // New Dashboard Types
  interface DashboardMetrics {
    totalUsers: number;
    activeUsers7d: number;
    totalKnowledgeBases: number;
    totalConversations: number;
    activeConversations7d: number;
    totalDocuments: number;
    documentsProcessed7d: number;
    activeAgents: number;
    activeServices: number;
    totalServices: number;
    userActivity: ActivityData[];
    apiUsage: ApiUsageData[];
    storageUsage: StorageData[];
    recentActivities: Activity[];
  }

  interface ActivityData {
    date: string;
    count: number;
  }

  interface ApiUsageData {
    date: string;
    requests: number;
  }

  interface StorageData {
    category: string;
    value: number;
  }

  interface Activity {
    id: string;
    type: 'user_created' | 'document_uploaded' | 'conversation' | 'settings_changed' | 'user_deleted';
    user: string;
    description: string;
    timestamp: string;
  }

  interface UserStats {
    total: number;
    active: number;
    new: number;
    byRole: {
      admin: number;
      user: number;
    };
    topActiveUsers: TopActiveUser[];
  }

  interface TopActiveUser {
    email: string;
    nickname: string;
    last_login: string;
  }

  interface SystemStats {
    cpu: {
      percent: number;
      count: number;
    };
    memory: {
      total: number;
      available: number;
      percent: number;
      used: number;
    };
    disk: {
      total: number;
      used: number;
      free: number;
      percent: number;
    };
    network: {
      connections: number;
    };
  }
}
