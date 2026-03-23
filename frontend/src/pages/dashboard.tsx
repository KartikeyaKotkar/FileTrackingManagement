import { useEffect, useState } from "react";
import { api } from "../services/api";
import { FileText, LogOut, LayoutDashboard, Settings, Search, RefreshCw, Plus, X } from "lucide-react";
import { useNavigate, Link, useLocation } from "react-router-dom";

interface Document {
  id: number;
  reference_no: string;
  title: string;
  department_id: number;
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
  const [newDept, setNewDept] = useState({ name: "" });
  const [createLoading, setCreateLoading] = useState(false);

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

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (!userData) {
      navigate("/login");
      return;
    }
    setUser(JSON.parse(userData));
    fetchDocs();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
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
    setCreateLoading(true);
    try {
      await api.post("/departments/", newDept);
      setCreateDeptModal(false);
      setNewDept({ name: "" });
      alert("Department created successfully!");
    } catch (err) {
      console.error(err);
      alert("Failed to create department.");
    } finally {
      setCreateLoading(false);
    }
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
                 <h2 className="text-2xl font-bold text-gray-900">{user?.role_id === 1 ? "Admin Dashboard" : "Dashboard"}</h2>
                 <p className="text-gray-500 text-sm mt-1">Welcome back, {user?.fullname || user?.username}. Here is your system overview.</p>
               </div>
               
               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                 <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
                   <h3 className="text-gray-500 text-sm font-medium mb-2">Total Documents</h3>
                   <span className="text-4xl font-bold text-gray-900">{documents.length || 0}</span>
                 </div>
                 {user?.role_id === 1 && (
                   <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
                     <h3 className="text-gray-500 text-sm font-medium mb-2">System Status</h3>
                     <span className="text-xl font-bold text-green-600 flex items-center gap-2">
                       <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
                       Healthy
                     </span>
                   </div>
                 )}
                 <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
                   <h3 className="text-gray-500 text-sm font-medium mb-2">Your Role</h3>
                   <span className="text-lg font-bold text-blue-600">{user?.role_id === 1 ? "Administrator" : "Standard User"}</span>
                 </div>
               </div>
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
                        <th className="px-6 py-4">Department ID</th>
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
                            <td className="px-6 py-4 text-gray-500">{doc.department_id}</td>
                            <td className="px-6 py-4">
                              <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${doc.status === 'Closed' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                                {doc.status || "Active"}
                              </span>
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
                <select value={newDoc.department_id} onChange={(e) => setNewDoc({...newDoc, department_id: Number(e.target.value)})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500">
                  <option value={1}>Admin</option>
                  <option value={2}>IT</option>
                  <option value={3}>Finance</option>
                  <option value={4}>HR</option>
                </select>
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setCreateModal(false)} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" disabled={createLoading} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50">Create</button>
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
              <h3 className="font-semibold text-lg">Create Department</h3>
              <button onClick={() => setCreateDeptModal(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5"/></button>
            </div>
            <form onSubmit={handleCreateDept} className="p-6 space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Department Name</label>
                <input required type="text" value={newDept.name} onChange={(e) => setNewDept({...newDept, name: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="Marketing" />
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setCreateDeptModal(false)} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" disabled={createLoading} className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50">Create Department</button>
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
