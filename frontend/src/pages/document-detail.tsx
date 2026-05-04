import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../services/api";
import { ArrowLeft, File, Send, History } from "lucide-react";

export default function DocumentDetail() {
  const { id } = useParams();
  const [doc, setDoc] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [transferStatus, setTransferStatus] = useState<any>(null);
  const [departmentsList, setDepartmentsList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [usersList, setUsersList] = useState<any[]>([]);

  // Forms
  const [newVersion, setNewVersion] = useState({ version_no: 1, file_name: "", file_path: "" });
  const [newMovement, setNewMovement] = useState({ to_dept: "", to_user_id: "" });
  
  const [editModal, setEditModal] = useState(false);
  const [editDoc, setEditDoc] = useState({ reference_no: "", tag_number: "", title: "" });
  const [editLoading, setEditLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [docRes, verRes, evtRes, trfRes, depRes, userRes] = await Promise.all([
        api.get(`/documents/${id}`),
        api.get(`/versions/${id}`),
        api.get(`/files/${id}/history`),
        api.get(`/files/${id}/transfer-status`),
        api.get(`/departments/?all=true`),
        api.get(`/auth/users`)
      ]);
      setDoc(docRes.data);
      setVersions(verRes.data);
      setEvents(evtRes.data);
      setTransferStatus(trfRes.data);
      setDepartmentsList(depRes.data);
      setUsersList(userRes.data);
      if (verRes.data.length > 0) {
        setNewVersion(prev => ({...prev, version_no: verRes.data[verRes.data.length - 1].version_no + 1}));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) setUser(JSON.parse(userData));
    fetchData();
  }, [id]);

  const handleCreateVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/versions/", {
        document_id: Number(id),
        ...newVersion,
        file_hash: "mock",
        file_size: 1024,
        created_by: user?.id || 1,
      });
      setNewVersion({...newVersion, file_name: "", file_path: "", version_no: newVersion.version_no + 1});
      fetchData();
    } catch (err) {
      console.error(err);
      alert("Failed to create version");
    }
  };

  const handleTransferRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMovement.to_dept) return;
    try {
      await api.post(`/files/${id}/request-transfer`, { 
        to_department_id: Number(newMovement.to_dept),
        to_user_id: newMovement.to_user_id ? Number(newMovement.to_user_id) : null
      });
      fetchData();
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to request transfer");
    }
  };

  const handleEditDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    setEditLoading(true);
    try {
      await api.put(`/documents/${id}`, editDoc);
      setEditModal(false);
      fetchData();
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to update document");
    } finally {
      setEditLoading(false);
    }
  };

  const openEditModal = () => {
    setEditDoc({
      reference_no: doc.reference_no,
      tag_number: doc.tag_number || "",
      title: doc.title
    });
    setEditModal(true);
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!doc) return <div className="p-8">Document not found</div>;

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-8">
      <Link to="/dashboard" className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-900 mb-6">
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to Dashboard
      </Link>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 text-left">
        {/* Left Column: Details & Versions */}
        <div className="lg:col-span-2 space-y-8">
          {/* Doc Header */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm relative">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{doc.title}</h1>
                <p className="text-gray-500 font-mono text-sm mt-1">
                  Ref: {doc.reference_no} 
                  {doc.tag_number && <span className="ml-4">Tag: {doc.tag_number}</span>}
                </p>
              </div>
              {(user?.role_id === 1 || user?.department_id === doc.department_id) && (
                <button onClick={openEditModal} className="text-blue-600 hover:text-blue-800 text-sm font-medium border border-blue-200 hover:bg-blue-50 px-3 py-1.5 rounded-md transition-colors">
                  Edit Details
                </button>
              )}
            </div>
            <div className="mt-4 flex gap-4">
              <span className="bg-blue-50 text-blue-700 text-xs font-semibold px-2.5 py-1 rounded-full">Dept: {doc.department?.name || doc.department_id || "Unassigned"}</span>
              <span className="bg-green-50 text-green-700 text-xs font-semibold px-2.5 py-1 rounded-full">{doc.status}</span>
            </div>
          </div>

          {/* Versions */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><File className="w-5 h-5"/> File Versions</h2>
            {versions.length > 0 ? (
              <ul className="space-y-3">
                {versions.map((v: any) => (
                  <li key={v.id} className="p-3 bg-gray-50 rounded-lg flex justify-between items-center border border-gray-100">
                    <div>
                      <span className="font-medium mr-2">v{v.version_no}</span>
                      <span className="text-sm text-gray-600">{v.file_name}</span>
                    </div>
                    <span className="text-xs text-gray-400">{new Date(v.created_at).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No versions uploaded yet.</p>
            )}
            
            <form onSubmit={handleCreateVersion} className="mt-6 pt-6 border-t border-gray-100 grid grid-cols-1 md:grid-cols-3 gap-3">
              <input required type="text" placeholder="File Name" value={newVersion.file_name} onChange={e => setNewVersion({...newVersion, file_name: e.target.value})} className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500" />
              <input required type="text" placeholder="File Path/URL" value={newVersion.file_path} onChange={e => setNewVersion({...newVersion, file_path: e.target.value})} className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500" />
              <button type="submit" className="bg-gray-900 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-gray-800">Add Version v{newVersion.version_no}</button>
            </form>
          </div>
        </div>

        {/* Right Column: Movement History */}
        <div className="space-y-8">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><Send className="w-5 h-5"/> Request Transfer</h2>
            {transferStatus ? (
              <div className="flex flex-col gap-3 text-sm font-medium p-6 bg-amber-50 rounded-xl border border-amber-200 text-amber-700 text-center items-center">
                <span className="text-3xl mb-1">⏳</span>
                <span className="bg-amber-100 px-3 py-1 rounded-full text-xs box-content border border-amber-200 shadow-sm">Pending Approval</span>
                <p className="text-amber-800 max-w-[200px]">Waiting for an admin to approve the transfer destination.</p>
              </div>
            ) : (
              <form onSubmit={handleTransferRequest} className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1.5 block">Transfer To Department</label>
                  <select required value={newMovement.to_dept} onChange={e => setNewMovement({to_dept: e.target.value, to_user_id: ""})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500 bg-gray-50">
                    <option value="" disabled>Select a destination</option>
                    {departmentsList.map(dep => (
                      <option key={dep.id} value={dep.id}>{dep.name}</option>
                    ))}
                  </select>
                </div>
                {newMovement.to_dept && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-1.5 block">Transfer To Person</label>
                    <select value={newMovement.to_user_id} onChange={e => setNewMovement({...newMovement, to_user_id: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500 bg-gray-50">
                      <option value="">Shared Inbox (Department)</option>
                      {usersList.filter((u: any) => u.department_id === Number(newMovement.to_dept)).map((u: any) => (
                        <option key={u.id} value={u.id}>{u.fullname || u.username}</option>
                      ))}
                    </select>
                  </div>
                )}
                <button type="submit" disabled={user?.role_id !== 1 && user?.department_id !== doc?.department_id} className="w-full bg-blue-600 text-white rounded-md px-4 py-3 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm">
                  Request Transfer
                </button>
                {user?.role_id !== 1 && user?.department_id !== doc?.department_id && (
                  <p className="text-xs text-red-500 text-center">You must own this document to request a transfer.</p>
                )}
              </form>
            )}
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><History className="w-5 h-5"/> Event History</h2>
            {events.length > 0 ? (
              <div className="relative border-l border-gray-200 ml-3 space-y-4">
                {events.map((e: any, idx: number) => (
                  <div key={idx} className="pl-4 relative">
                    <div className="absolute w-2 h-2 bg-blue-500 rounded-full -left-[4.5px] top-1.5 ring-4 ring-white"></div>
                    <p className="text-sm font-medium capitalize">Document {e.action}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      By {e.performed_by || "System"} 
                      {e.action === "moved" && e.to_department && ` (${e.from_department || "?"} → ${e.to_department})`}
                      {e.approved_by && ` (Approved by ${e.approved_by})`}
                      <br/>
                      {new Date(e.timestamp).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No event history.</p>
            )}
          </div>
        </div>
      </div>
    
    {editModal && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 p-4">
        <div className="bg-white rounded-xl shadow-lg w-full max-w-md overflow-hidden relative">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 className="font-semibold text-lg">Edit Document</h3>
            <button onClick={() => setEditModal(false)} className="text-gray-400 hover:text-gray-600">×</button>
          </div>
          <form onSubmit={handleEditDocument} className="p-6 space-y-4">
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">Reference Number</label>
              <input required type="text" value={editDoc.reference_no} onChange={(e) => setEditDoc({...editDoc, reference_no: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">Tag Number</label>
              <input type="text" value={editDoc.tag_number} onChange={(e) => setEditDoc({...editDoc, tag_number: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">Title</label>
              <input required type="text" value={editDoc.title} onChange={(e) => setEditDoc({...editDoc, title: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div className="pt-4 flex justify-end gap-3">
              <button type="button" onClick={() => setEditModal(false)} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
              <button type="submit" disabled={editLoading} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50">Save Changes</button>
            </div>
          </form>
        </div>
      </div>
    )}
  </div>
  );
}
