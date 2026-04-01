import { useEffect, useState } from "react";
import { api } from "../services/api";
import { FileText, LogOut, LayoutDashboard, Settings, Search, RefreshCw, Plus, X, Send } from "lucide-react";
import { useNavigate, Link, useLocation } from "react-router-dom";

interface Document {
  id: number;
  reference_no: string;
  title: string;
  department_id: number;
  department?: { id: number; name: string };
  created_by: number;
  status: string;
  created_at: string;
}

export default function Dashboard() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [createModal, setCreateModal] = useState(false);
  const [createUserModal, setCreateUserModal] = useState(false);
  const [createDeptModal, setCreateDeptModal] = useState(false);
  
  // Create state
  const [newDoc, setNewDoc] = useState({ reference_no: "", title: "", department_id: 1 });
  const [newUser, setNewUser] = useState({ username: "", password: "", role: "user" });
  const [newDept, setNewDept] = useState({ name: "", description: "" });
  const [createLoading, setCreateLoading] = useState(false);
  const [editingDeptId, setEditingDeptId] = useState<number | null>(null);

  // Admin explicit states
  const [adminStats, setAdminStats] = useState<any>(null);
  const [adminLogs, setAdminLogs] = useState<any[]>([]);
  const [departmentsList, setDepartmentsList] = useState<any[]>([]);
  const [usersList, setUsersList] = useState<any[]>([]);
  const [pendingTransfers, setPendingTransfers] = useState<any[]>([]);
  
  // Assignment state
  const [assignDeptModal, setAssignDeptModal] = useState<number | null>(null);
  const [selectedDeptId, setSelectedDeptId] = useState<number | "">("");

  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res = await api.get("/documents/");
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserDepartment = async () => {
    try {
      const res = await api.get("/departments/");
      if (res.data && res.data.length > 0) {
        setDepartmentsList(res.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (!userData) {
      navigate("/login");
      return;
    }
    const parsedUser = JSON.parse(userData);
    setUser(parsedUser);
    fetchDocs();
    fetchUserDepartment();

    if (parsedUser.role_id === 1) {
      const fetchAdminData = async () => {
        try {
          const [statsRes, logsRes, transfersRes] = await Promise.all([
            api.get("/admin/dashboard"),
            api.get("/admin/logs"),
            api.get("/transfer/pending")
          ]);
          setAdminStats(statsRes.data);
          setAdminLogs(logsRes.data);
          setPendingTransfers(transfersRes.data);
          
          if (currentPath === "/departments-view") {
              const deptsRes = await api.get("/departments/");
              setDepartmentsList(deptsRes.data);
          }

          if (currentPath === "/users-view") {
              const [usersRes, deptsRes] = await Promise.all([
                  api.get("/auth/users"),
                  api.get("/departments/")
              ]);
              setUsersList(usersRes.data);
              setDepartmentsList(deptsRes.data);
          }
        } catch (err) {
          console.error(err);
        }
      };
      fetchAdminData();
    } else {
      const fetchUserData = async () => {
        try {
          const logsRes = await api.get("/files/department-logs");
          setAdminLogs(logsRes.data);
        } catch (err) {
          console.error(err);
        }
      };
      fetchUserData();
    }
  }, [navigate, currentPath]);

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  const handleStatusChange = async (id: number, newStatus: string) => {
    try {
      await api.patch(`/documents/${id}/status`, { status: newStatus });
      fetchDocs();
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to update status.");
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateLoading(true);
    try {
      await api.post("/documents/", {
        ...newDoc,
        created_by: user?.id || 1,
      });
      setCreateModal(false);
      setNewDoc({ reference_no: "", title: "", department_id: 1 });
      fetchDocs();
    } catch (err) {
      console.error(err);
      alert("Failed to create document.");
    } finally {
      setCreateLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateLoading(true);
    try {
      await api.post("/auth/users", newUser);
      setCreateUserModal(false);
      setNewUser({ username: "", password: "", role: "user" });
      alert("User created successfully!");
    } catch (err) {
      console.error(err);
      alert("Failed to create user.");
    } finally {
      setCreateLoading(false);
    }
  };

  const handleCreateDept = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDept.name.trim()) {
       alert("Department name cannot be empty");
       return;
    }
    
    setCreateLoading(true);
    try {
      if (editingDeptId) {
        await api.put(`/departments/${editingDeptId}`, { name: newDept.name, description: newDept.description });
        alert("Department updated successfully!");
      } else {
        await api.post("/departments/", { name: newDept.name, description: newDept.description });
        alert("Department created successfully!");
      }
      setCreateDeptModal(false);
      setEditingDeptId(null);
      setNewDept({ name: "", description: "" });
      
      if (currentPath === "/departments-view") {
          const deptsRes = await api.get("/departments/");
          setDepartmentsList(deptsRes.data);
      }
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to save department. Please try again.");
    } finally {
      setCreateLoading(false);
    }
  };

  const handleEditDeptClick = (dep: any) => {
    setEditingDeptId(dep.id);
    setNewDept({ name: dep.name, description: dep.description || "" });
    setCreateDeptModal(true);
  };

  const handleDeleteDept = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this department?")) return;
    try {
      await api.delete(`/departments/${id}`);
      const deptsRes = await api.get("/departments/");
      setDepartmentsList(deptsRes.data);
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to delete department.");
    }
  };

  const handleCloseDeptModal = () => {
    setCreateDeptModal(false);
    setEditingDeptId(null);
    setNewDept({ name: "", description: "" });
  };

  const handleAssignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignDeptModal || !selectedDeptId) return;
    setCreateLoading(true);
    try {
      await api.put(`/auth/users/${assignDeptModal}/assign-department`, { department_id: Number(selectedDeptId) });
      alert("User assigned successfully!");
      setAssignDeptModal(null);
      setSelectedDeptId("");
      const usersRes = await api.get("/auth/users");
      setUsersList(usersRes.data);
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to assign user.");
    } finally {
      setCreateLoading(false);
    }
  };

  const renderPieChart = () => {
    if (!adminStats || !adminStats.movement_counts_by_action) return null;
    const total = adminStats.movement_counts_by_action.reduce((sum: number, a: any) => sum + a.count, 0) || 1;
    let acc = 0;
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#6366f1'];
    const stops = adminStats.movement_counts_by_action.map((a: any, i: number) => {
        const start = acc;
        acc += (a.count / total) * 100;
        return `${colors[i % colors.length]} ${start}% ${acc}%`;
    }).join(', ');
    
    return (
        <div className="flex items-center gap-8 pl-4">
            <div className="w-28 h-28 rounded-full border-4 border-white shadow-sm flex-shrink-0" style={{ background: stops ? `conic-gradient(${stops})` : '#f3f4f6' }}></div>
            <div className="flex flex-col gap-2">
                {adminStats.movement_counts_by_action.map((a: any, i: number) => (
                    <div key={a.action} className="flex items-center gap-2 text-sm">
                        <span className="w-3 h-3 rounded-full" style={{ backgroundColor: colors[i % colors.length] }}></span>
                        <span className="capitalize text-gray-700 font-medium">{a.action} ({a.count})</span>
                    </div>
                ))}
            </div>
        </div>
    );
  };

  return (
    <div className="min-h-screen w-full bg-gray-50 text-gray-900 flex font-sans overflow-hidden text-left">
      {/* Sidebar */}
      <aside className="w-20 lg:w-64 border-r border-gray-200 bg-white flex flex-col transition-all duration-300">
        <div className="h-20 flex items-center justify-center lg:justify-start lg:px-8 border-b border-gray-200">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600 font-bold text-xl">
            FT
          </div>
          <span className="hidden lg:block ml-3 font-semibold text-lg tracking-tight text-gray-800">Tracker</span>
        </div>

        <nav className="flex-1 py-6 flex flex-col gap-2 px-3">
          <NavItem to="/dashboard" icon={<LayoutDashboard />} label={user?.role_id === 1 ? "Admin Dashboard" : "Dashboard"} active={currentPath === "/dashboard"} />
          <NavItem to="/documents" icon={<FileText />} label="Documents" active={currentPath === "/documents"} />
          {user?.role_id === 1 && (
            <>
             <NavItem to="/users-view" icon={<LayoutDashboard />} label="Users" active={currentPath === "/users-view"} />
             <NavItem to="/departments-view" icon={<LayoutDashboard />} label="Departments" active={currentPath === "/departments-view"} />
             <NavItem to="/transfers-view" icon={<Send />} label="Pending Transfers" active={currentPath === "/transfers-view"} />
            </>
          )}
          <NavItem to="/settings" icon={<Settings />} label="Settings" active={currentPath === "/settings"} />
        </nav>

        <div className="p-4 border-t border-gray-200">
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center lg:justify-start gap-3 p-3 rounded-xl text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-all font-medium group"
          >
            <LogOut className="w-5 h-5" />
            <span className="hidden lg:block">Log Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-y-auto w-full">
        <header className="h-20 border-b border-gray-200 bg-white flex items-center justify-between px-8 sticky top-0 z-20">
          <h1 className="text-xl font-medium tracking-tight">Overview</h1>
          <div className="flex items-center gap-4">
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input 
                type="text" 
                placeholder="Search..." 
                className="bg-gray-50 border border-gray-200 rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all w-64 text-gray-700 placeholder:text-gray-400"
              />
            </div>
          </div>
        </header>

        <div className="flex-1 p-8 z-10 w-full max-w-6xl mx-auto">
          
          {/* Dashboard Tab */}
          {currentPath === "/dashboard" && (
            <div className="space-y-8 animate-in fade-in duration-300">
               <div>
                 <h2 className="text-2xl font-bold text-gray-900">{user?.role_id === 1 ? "Admin Monitoring Panel" : "Dashboard"}</h2>
                 <p className="text-gray-500 text-sm mt-1">Welcome back, {user?.fullname || user?.username}. Here is your system overview.</p>
               </div>
               
               {user?.role_id === 1 && adminStats ? (
                 <div className="space-y-6">
                   <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                     <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                       <h3 className="text-lg font-bold text-gray-900 mb-6">Action Volume Distribution</h3>
                       {renderPieChart()}
                     </div>
                     <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                       <h3 className="text-lg font-bold text-gray-900 mb-6">Department Moves</h3>
                       <div className="space-y-4">
                         {adminStats.movement_counts_by_department.length === 0 && <p className="text-sm text-gray-500">No departmental movements yet.</p>}
                         {adminStats.movement_counts_by_department.map((d: any) => (
                           <div key={d.department} className="flex justify-between items-center text-sm">
                             <span className="text-gray-600 w-24 truncate font-medium">{d.department}:</span>
                             <div className="flex-1 ml-2 h-2.5 bg-gray-100 rounded-full overflow-hidden">
                               <div className="h-full bg-indigo-500 rounded-full transition-all" style={{ width: `${Math.min((d.count / (adminLogs.length || 1)) * 100, 100)}%` }}></div>
                             </div>
                             <span className="ml-3 font-mono text-gray-500">{d.count}</span>
                           </div>
                         ))}
                       </div>
                     </div>
                   </div>

                   <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                     <div className="p-6 border-b border-gray-100">
                        <h3 className="text-lg font-bold text-gray-900">Recent File Activity</h3>
                     </div>
                     <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                          <thead className="bg-gray-50 text-gray-500 font-medium">
                            <tr>
                              <th className="px-6 py-3 whitespace-nowrap">Time</th>
                              <th className="px-6 py-3">Action</th>
                              <th className="px-6 py-3">User</th>
                              <th className="px-6 py-3">File ID</th>
                              <th className="px-6 py-3">Approved By</th>
                              <th className="px-6 py-3">Details</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {adminLogs.map((log: any, i: number) => (
                              <tr key={i} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-3 text-xs text-gray-500 whitespace-nowrap">{new Date(log.timestamp).toLocaleString()}</td>
                                <td className="px-6 py-3 font-medium capitalize text-gray-900">{log.action}</td>
                                <td className="px-6 py-3 text-gray-600">{log.performed_by || 'System'}</td>
                                <td className="px-6 py-3 font-mono text-gray-500 text-xs">
                                  #{log.file_id} {log.file_name ? `- ${log.file_name}` : ''}
                                </td>
                                <td className="px-6 py-3 text-gray-600">
                                  {log.approved_by || '-'}
                                </td>
                                <td className="px-6 py-3 text-gray-600">
                                  {log.action === "moved" 
                                    ? `${log.from_department || '?'} → ${log.to_department}` 
                                    : log.action === "created" 
                                      ? `Created document: ${log.file_name || 'Unknown'}`
                                      : '-'}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        {adminLogs.length === 0 && <div className="p-12 text-center text-sm text-gray-500">No events found in the database.</div>}
                     </div>
                   </div>
                 </div>
               ) : (
                 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                   <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
                     <h3 className="text-gray-500 text-sm font-medium mb-2">Total Documents</h3>
                     <span className="text-4xl font-bold text-gray-900">{documents.length || 0}</span>
                   </div>
                   <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
                     <h3 className="text-gray-500 text-sm font-medium mb-2">Your Role</h3>
                     <span className="text-lg font-bold text-blue-600">{user?.role_id === 1 ? "Administrator" : "Standard User"}</span>
                   </div>

                   <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden md:col-span-2 lg:col-span-3">
                     <div className="p-6 border-b border-gray-100">
                        <h3 className="text-lg font-bold text-gray-900">Recent Department Activity</h3>
                     </div>
                     <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                          <thead className="bg-gray-50 text-gray-500 font-medium">
                            <tr>
                              <th className="px-6 py-3 whitespace-nowrap">Time</th>
                              <th className="px-6 py-3">Action</th>
                              <th className="px-6 py-3">User</th>
                              <th className="px-6 py-3">File ID</th>
                              <th className="px-6 py-3">Approved By</th>
                              <th className="px-6 py-3">Details</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {adminLogs.map((log: any, i: number) => (
                              <tr key={i} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-3 text-xs text-gray-500 whitespace-nowrap">{new Date(log.timestamp).toLocaleString()}</td>
                                <td className="px-6 py-3 font-medium capitalize text-gray-900">{log.action}</td>
                                <td className="px-6 py-3 text-gray-600">{log.performed_by || 'System'}</td>
                                <td className="px-6 py-3 font-mono text-gray-500 text-xs">
                                  #{log.file_id} {log.file_name ? `- ${log.file_name}` : ''}
                                </td>
                                <td className="px-6 py-3 text-gray-600">
                                  {log.approved_by || '-'}
                                </td>
                                <td className="px-6 py-3 text-gray-600">
                                  {log.action === "moved" 
                                    ? `${log.from_department || '?'} → ${log.to_department}` 
                                    : log.action === "created" 
                                      ? `Created document: ${log.file_name || 'Unknown'}`
                                      : '-'}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        {adminLogs.length === 0 && <div className="p-12 text-center text-sm text-gray-500">No events found for your department.</div>}
                     </div>
                   </div>
                 </div>
               )}
            </div>
          )}

          {/* Documents Tab */}
          {currentPath === "/documents" && (
            <div className="animate-in fade-in duration-300">
              <div className="flex items-end justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Recent Documents</h2>
                  <p className="text-gray-500 mt-1 text-sm">Manage and track your organization's files.</p>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={fetchDocs}
                    className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg text-sm font-medium transition-colors text-gray-700"
                  >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                  </button>
                  <button 
                    onClick={() => setCreateModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    New Document
                  </button>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm whitespace-nowrap">
                    <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-medium tracking-wide">
                      <tr>
                        <th className="px-6 py-4">Ref No</th>
                        <th className="px-6 py-4">Title</th>
                        <th className="px-6 py-4">Department</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {loading ? (
                        <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Loading...</td></tr>
                      ) : documents.length > 0 ? (
                        documents.map((doc) => (
                          <tr key={doc.id} className="hover:bg-gray-50 transition-colors group">
                            <td className="px-6 py-4 font-mono text-gray-600">{doc.reference_no}</td>
                            <td className="px-6 py-4 font-medium text-gray-900">{doc.title}</td>
                            <td className="px-6 py-4 text-gray-500">{doc.department?.name || doc.department_id || "Unassigned"}</td>
                            <td className="px-6 py-4">
                              {user?.role_id === 1 ? (
                                <select 
                                  value={doc.status || "Active"} 
                                  onChange={(e) => handleStatusChange(doc.id, e.target.value)}
                                  className={`px-2.5 py-1 text-xs font-medium rounded-full cursor-pointer focus:ring-2 focus:ring-blue-500 border border-transparent hover:border-gray-200 transition-colors ${doc.status === 'Closed' ? 'bg-red-50 text-red-600' : doc.status === 'Pending Transfer' ? 'bg-yellow-50 text-yellow-600' : 'bg-green-50 text-green-600'}`}
                                >
                                  <option value="Active" className="bg-white text-gray-900">Active</option>
                                  <option value="Pending Transfer" className="bg-white text-gray-900">Pending Transfer</option>
                                  <option value="Closed" className="bg-white text-gray-900">Closed</option>
                                </select>
                              ) : (
                                <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${doc.status === 'Closed' ? 'bg-red-50 text-red-600' : doc.status === 'Pending Transfer' ? 'bg-yellow-50 text-yellow-600' : 'bg-green-50 text-green-600'}`}>
                                  {doc.status || "Active"}
                                </span>
                              )}
                            </td>
                            <td className="px-6 py-4 text-right">
                              <Link to={`/documents/${doc.id}`} className="text-blue-600 hover:text-blue-700 font-medium hover:underline">View details</Link>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                            No documents found
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Settings Tab */}
          {currentPath === "/settings" && (
            <div className="space-y-6 animate-in fade-in duration-300">
               <div>
                 <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
                 <p className="text-gray-500 text-sm mt-1">Manage your account and system preferences.</p>
               </div>
               
               {user?.role_id === 1 ? (
                 <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                   <h3 className="text-lg font-bold text-gray-900 mb-4">Admin Control Panel</h3>
                   <div className="flex gap-4">
                     <button onClick={() => setCreateUserModal(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors">
                       Create User
                     </button>
                     <button onClick={() => setCreateDeptModal(true)} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors">
                       Create Department
                     </button>
                   </div>
                   <p className="text-sm text-gray-500 mt-4">These actions are strictly protected by backend RBAC and will fail if accessed by non-admins.</p>
                 </div>
               ) : (
                 <div className="bg-white p-12 rounded-xl border border-gray-200 shadow-sm text-center">
                    <Settings className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-gray-900 mb-2">Personal Settings</h3>
                    <p className="text-gray-500">Regular user settings and preferences are currently under development.</p>
                 </div>
               )}
            </div>
          )}

          {/* Departments View Tab */}
          {currentPath === "/departments-view" && (
            <div className="animate-in fade-in duration-300">
              <div className="flex items-end justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Departments</h2>
                  <p className="text-gray-500 mt-1 text-sm">View all departments you have created.</p>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={() => {
                      setEditingDeptId(null);
                      setNewDept({ name: "", description: "" });
                      setCreateDeptModal(true);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    New Department
                  </button>
                </div>
              </div>
              
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-medium">
                    <tr>
                      <th className="px-6 py-4">Name</th>
                      <th className="px-6 py-4">Description</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {departmentsList.map((dep: any) => (
                      <tr key={dep.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">{dep.name}</td>
                        <td className="px-6 py-4 text-gray-600">{dep.description || "No description"}</td>
                        <td className="px-6 py-4 text-right">
                          <button onClick={() => handleEditDeptClick(dep)} className="text-blue-600 hover:text-blue-800 font-medium mr-4">Edit</button>
                          <button onClick={() => handleDeleteDept(dep.id)} className="text-red-600 hover:text-red-800 font-medium">Delete</button>
                        </td>
                      </tr>
                    ))}
                    {departmentsList.length === 0 && (
                      <tr>
                        <td colSpan={3} className="px-6 py-12 text-center text-gray-500">
                          You haven't created any departments yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Users View Tab */}
          {currentPath === "/users-view" && (
            <div className="animate-in fade-in duration-300">
              <div className="flex items-end justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Users</h2>
                  <p className="text-gray-500 mt-1 text-sm">View all users and assign them to your departments.</p>
                </div>
              </div>
              
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-medium">
                    <tr>
                      <th className="px-6 py-4">Username</th>
                      <th className="px-6 py-4">Fullname</th>
                      <th className="px-6 py-4">Role</th>
                      <th className="px-6 py-4">Department</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {usersList.map((u: any) => (
                      <tr key={u.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">{u.username}</td>
                        <td className="px-6 py-4 text-gray-600">{u.fullname}</td>
                        <td className="px-6 py-4 text-gray-600 capitalize">{u.role_id === 1 ? 'admin' : 'user'}</td>
                        <td className="px-6 py-4 text-gray-600">{u.department_name || "Unassigned"}</td>
                        <td className="px-6 py-4 text-right">
                          <button onClick={() => setAssignDeptModal(u.id)} className="text-blue-600 hover:text-blue-800 font-medium">Assign Department</button>
                        </td>
                      </tr>
                    ))}
                    {usersList.length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                          No users found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Transfers View Tab */}
          {currentPath === "/transfers-view" && (
            <div className="animate-in fade-in duration-300">
              <div className="flex items-end justify-between mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Pending Transfers</h2>
                  <p className="text-gray-500 mt-1 text-sm">Review and approve document transfer requests.</p>
                </div>
              </div>
              
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-medium">
                    <tr>
                      <th className="px-6 py-4">Document</th>
                      <th className="px-6 py-4">Requested By</th>
                      <th className="px-6 py-4">Route</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {pendingTransfers.map((t: any) => (
                      <tr key={t.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">
                           {t.document_title} <span className="text-xs text-gray-500 block">{t.reference_no}</span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">{t.requested_by_name}</td>
                        <td className="px-6 py-4 text-gray-600">
                           {t.from_department_name} <span className="font-bold mx-1 text-gray-300">→</span> {t.to_department_name}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button onClick={async () => {
                              await api.post(`/transfer/${t.id}/approve`);
                              const res = await api.get("/transfer/pending");
                              setPendingTransfers(res.data);
                          }} className="px-3 py-1.5 bg-green-50 text-green-600 hover:bg-green-100 font-medium rounded-md mr-2">Approve</button>

                          <button onClick={async () => {
                              await api.post(`/transfer/${t.id}/reject`);
                              const res = await api.get("/transfer/pending");
                              setPendingTransfers(res.data);
                          }} className="px-3 py-1.5 bg-red-50 text-red-600 hover:bg-red-100 font-medium rounded-md">Reject</button>
                        </td>
                      </tr>
                    ))}
                    {pendingTransfers.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                          No pending transfers found. All sorted!
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Create Modal */}
      {createModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 p-4">
          <div className="bg-white rounded-xl shadow-lg w-full max-w-md overflow-hidden relative">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 className="font-semibold text-lg">Create Document</h3>
              <button onClick={() => setCreateModal(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5"/></button>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Reference Number</label>
                <input required type="text" value={newDoc.reference_no} onChange={(e) => setNewDoc({...newDoc, reference_no: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="DOC-2024-001" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Title</label>
                <input required type="text" value={newDoc.title} onChange={(e) => setNewDoc({...newDoc, title: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="Project Proposal" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Department</label>
                {user?.role_id === 1 ? (
                   <select value={newDoc.department_id} onChange={(e) => setNewDoc({...newDoc, department_id: Number(e.target.value)})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500">
                     <option value={0} disabled>Select Department</option>
                     {departmentsList.map(dep => (
                         <option key={dep.id} value={dep.id}>{dep.name}</option>
                     ))}
                   </select>
                ) : (
                   <div className="w-full border border-gray-200 bg-gray-50 text-gray-500 rounded-md px-3 py-2 text-sm">
                      Department: {user?.department_name || departmentsList?.[0]?.name || "Unassigned"}
                   </div>
                )}
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setCreateModal(false)} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" disabled={createLoading || (!user?.department_id && user?.role_id !== 1)} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create User Modal */}
      {createUserModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 p-4">
          <div className="bg-white rounded-xl shadow-lg w-full max-w-md overflow-hidden relative">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 className="font-semibold text-lg">Create New User</h3>
              <button onClick={() => setCreateUserModal(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5"/></button>
            </div>
            <form onSubmit={handleCreateUser} className="p-6 space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Username</label>
                <input required type="text" value={newUser.username} onChange={(e) => setNewUser({...newUser, username: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="jane.doe" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Password</label>
                <input required type="password" value={newUser.password} onChange={(e) => setNewUser({...newUser, password: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="••••••••" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Role</label>
                <select value={newUser.role} onChange={(e) => setNewUser({...newUser, role: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500">
                  <option value="user">Standard User</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setCreateUserModal(false)} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" disabled={createLoading} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50">Create User</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Department Modal */}
      {createDeptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 p-4">
          <div className="bg-white rounded-xl shadow-lg w-full max-w-md overflow-hidden relative">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 className="font-semibold text-lg">{editingDeptId ? "Edit Department" : "Create Department"}</h3>
              <button onClick={handleCloseDeptModal} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5"/></button>
            </div>
            <form onSubmit={handleCreateDept} className="p-6 space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Department Name</label>
                <input required type="text" value={newDept.name} onChange={(e) => setNewDept({...newDept, name: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="Marketing" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Division (Optional Placeholder)</label>
                <input type="text" className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="Global Operations" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Description</label>
                <input type="text" value={newDept.description} onChange={(e) => setNewDept({...newDept, description: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="Handles internal..." />
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={handleCloseDeptModal} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" disabled={createLoading} className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50">
                   {editingDeptId ? "Update Department" : "Create Department"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Assign User Modal */}
      {assignDeptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 p-4">
          <div className="bg-white rounded-xl shadow-lg w-full max-w-md overflow-hidden relative">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 className="font-semibold text-lg">Assign Department</h3>
              <button onClick={() => setAssignDeptModal(null)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5"/></button>
            </div>
            <form onSubmit={handleAssignSubmit} className="p-6 space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Select Department</label>
                <select required value={selectedDeptId} onChange={(e) => setSelectedDeptId(Number(e.target.value))} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500">
                  <option value="" disabled>Select a department</option>
                  {departmentsList.map(d => (
                     <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
                {departmentsList.length === 0 && <p className="text-xs text-red-500 mt-2">You haven't created any departments yet.</p>}
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setAssignDeptModal(null)} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" disabled={createLoading || !selectedDeptId} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50">
                   Confirm Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function NavItem({ icon, label, active = false, to }: { icon: React.ReactNode, label: string, active?: boolean, to: string }) {
  return (
    <Link to={to} className={`w-full flex items-center justify-center lg:justify-start gap-3 p-3 rounded-xl transition-all font-medium grid-cols-2 relative ${
      active 
        ? 'text-blue-600 bg-blue-50' 
        : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'
    }`}>
      {icon}
      <span className="hidden lg:block text-sm">{label}</span>
    </Link>
  );
}
