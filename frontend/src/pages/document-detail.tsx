import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../services/api";
import { ArrowLeft, File, Send, History } from "lucide-react";

export default function DocumentDetail() {
  const { id } = useParams();
  const [doc, setDoc] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [movements, setMovements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  // Forms
  const [newVersion, setNewVersion] = useState({ version_no: 1, file_name: "", file_path: "" });
  const [newMovement, setNewMovement] = useState({ to_dept: 1, remarks: "" });

  const fetchData = async () => {
    try {
      const [docRes, verRes, movRes] = await Promise.all([
        api.get(`/documents/${id}`),
        api.get(`/versions/${id}`),
        api.get(`/movement/${id}`)
      ]);
      setDoc(docRes.data);
      setVersions(verRes.data);
      setMovements(movRes.data);
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

  const handleMove = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/movement/", {
        document_id: Number(id),
        from_dept: doc?.department_id || 1, // simplified assumption
        to_dept: Number(newMovement.to_dept),
        movement_type: "Transfer",
        approved_by: user?.id || 1,
        moved_by: user?.id || 1,
        remarks: newMovement.remarks
      });
      setNewMovement({to_dept: 1, remarks: ""});
      fetchData();
    } catch (err) {
      console.error(err);
      alert("Failed to move document");
    }
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
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h1 className="text-2xl font-bold text-gray-900">{doc.title}</h1>
            <p className="text-gray-500 font-mono text-sm mt-1">{doc.reference_no}</p>
            <div className="mt-4 flex gap-4">
              <span className="bg-blue-50 text-blue-700 text-xs font-semibold px-2.5 py-1 rounded-full">Dept: {doc.department_id}</span>
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
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><Send className="w-5 h-5"/> Transfer Document</h2>
            <form onSubmit={handleMove} className="space-y-3">
              <div>
                <label className="text-sm text-gray-600 mb-1 block">To Department</label>
                <select value={newMovement.to_dept} onChange={e => setNewMovement({...newMovement, to_dept: Number(e.target.value)})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500">
                  <option value={1}>Admin</option>
                  <option value={2}>IT</option>
                  <option value={3}>Finance</option>
                  <option value={4}>HR</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-600 mb-1 block">Remarks</label>
                <input type="text" value={newMovement.remarks} onChange={e => setNewMovement({...newMovement, remarks: e.target.value})} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500" placeholder="Transfer reason..." />
              </div>
              <button type="submit" className="w-full bg-blue-600 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-blue-700">Submit Transfer</button>
            </form>
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><History className="w-5 h-5"/> Movement History</h2>
            {movements.length > 0 ? (
              <div className="relative border-l border-gray-200 ml-3 space-y-4">
                {movements.map((m: any) => (
                  <div key={m.id} className="pl-4 relative">
                    <div className="absolute w-2 h-2 bg-blue-500 rounded-full -left-[4.5px] top-1.5 ring-4 ring-white"></div>
                    <p className="text-sm font-medium">Moved to Dept {m.to_department_id}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{m.remarks || "No remarks"} • {new Date(m.moved_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No movement history.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
