"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { ChevronLeft, ChevronRight, Save, ShieldCheck, Image as ImageIcon, Type, HelpCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function ReviewPage() {
  const params = useParams();
  const documentId = params.id as string;
  
  const [doc, setDoc] = useState<any>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    api.getCanonicalOutput(documentId).then(setDoc);
  }, [documentId]);

  if (!doc) return <div className="p-8">Loading document...</div>;

  const page = doc.pages[currentPage];

  const handleSaveOverride = async (updates: any) => {
    if (!selectedItem) return;
    setIsSaving(true);
    try {
      const id = selectedItem.block_id || selectedItem.field_id;
      await api.applyReviewAction(documentId, id, updates);
      // Refresh local state
      const updatedDoc = { ...doc };
      const page = updatedDoc.pages[currentPage];
      
      if (selectedItem.field_id) {
        const form = page.forms.find((f: any) => f.field_id === selectedItem.field_id);
        Object.assign(form, updates);
        setSelectedItem({ ...form });
      } else {
        const block = page.blocks.find((b: any) => b.block_id === selectedItem.block_id);
        Object.assign(block, updates);
        setSelectedItem({ ...block });
      }
      setDoc(updatedDoc);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <a href="/" className="text-gray-500 hover:text-gray-900"><ChevronLeft /></a>
          <h1 className="text-xl font-bold">Review: {doc.document_id.slice(0, 8)}</h1>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span>Page {currentPage + 1} of {doc.page_count}</span>
          <div className="flex gap-1">
            <button 
              onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
              disabled={currentPage === 0}
              className="p-1 rounded hover:bg-gray-100 disabled:opacity-30"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button 
              onClick={() => setCurrentPage(Math.min(doc.page_count - 1, currentPage + 1))}
              disabled={currentPage === doc.page_count - 1}
              className="p-1 rounded hover:bg-gray-100 disabled:opacity-30"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* PDF View Area (Simplified Mock) */}
        <div className="flex-1 overflow-auto p-8 flex justify-center">
          <div 
            className="bg-white shadow-lg relative border border-gray-300"
            style={{ width: page.width, height: page.height, transform: "scale(0.8)", transformOrigin: "top center" }}
          >
            {/* Render Blocks */}
            {page.blocks.map((block: any) => (
              <div
                key={block.block_id}
                onClick={() => setSelectedItem(block)}
                className={`absolute cursor-pointer border-2 transition-all ${
                  selectedItem?.block_id === block.block_id 
                    ? "border-blue-500 bg-blue-50/30 ring-2 ring-blue-200" 
                    : "border-transparent hover:border-blue-300 hover:bg-blue-50/10"
                }`}
                style={{
                  left: block.bbox.x0,
                  top: block.bbox.y0,
                  width: block.bbox.x1 - block.bbox.x0,
                  height: block.bbox.y1 - block.bbox.y0,
                }}
                title={block.role}
              >
                {selectedItem?.block_id === block.block_id && (
                  <div className="absolute -top-6 left-0 bg-blue-600 text-white text-[10px] px-1 rounded whitespace-nowrap">
                    {block.role}
                  </div>
                )}
              </div>
            ))}

            {/* Render Forms */}
            {page.forms.map((form: any) => (
              <div
                key={form.field_id}
                onClick={() => setSelectedItem(form)}
                className={`absolute cursor-pointer border-2 transition-all rounded ${
                  selectedItem?.field_id === form.field_id 
                    ? "border-purple-500 bg-purple-50/30 ring-2 ring-purple-200" 
                    : "border-purple-300/50 hover:border-purple-500 hover:bg-purple-50/10"
                }`}
                style={{
                  left: form.bbox.x0,
                  top: form.bbox.y0,
                  width: form.bbox.x1 - form.bbox.x0,
                  height: form.bbox.y1 - form.bbox.y0,
                }}
                title={`Form: ${form.name}`}
              >
                <div className="absolute -top-5 right-0 bg-purple-600 text-white text-[8px] px-1 rounded">
                  FORM
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar Inspector */}
        <div className="w-96 bg-white border-l overflow-auto p-6">
          {selectedItem ? (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <ShieldCheck className={`w-5 h-5 ${selectedItem.field_id ? 'text-purple-600' : 'text-blue-600'}`} /> 
                {selectedItem.field_id ? 'Form Field Inspector' : 'Block Inspector'}
              </h2>
              
              <div className="p-3 bg-gray-50 rounded-lg font-mono text-xs break-all">
                ID: {selectedItem.block_id || selectedItem.field_id}
              </div>

              {!selectedItem.field_id && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Type className="w-4 h-4" /> Semantic Role
                  </label>
                  <select 
                    value={selectedItem.role}
                    onChange={(e) => handleSaveOverride({ role: e.target.value })}
                    className="w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  >
                    <option value="heading1">Heading 1</option>
                    <option value="heading2">Heading 2</option>
                    <option value="heading3">Heading 3</option>
                    <option value="text">Paragraph</option>
                    <option value="list_item">List Item</option>
                    <option value="figure">Figure</option>
                    <option value="artifact">Artifact (Decorative)</option>
                  </select>
                </div>
              )}

              {selectedItem.role === "figure" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <ImageIcon className="w-4 h-4" /> Alternative Text
                  </label>
                  <textarea 
                    value={selectedItem.alt_text || ""}
                    onChange={(e) => setSelectedItem({ ...selectedItem, alt_text: e.target.value })}
                    className="w-full rounded-md border-gray-300 shadow-sm p-2 border h-32"
                    placeholder="Describe the image..."
                  />
                  <button 
                    onClick={() => handleSaveOverride({ alt_text: selectedItem.alt_text })}
                    className="mt-2 w-full bg-gray-800 text-white py-2 rounded flex items-center justify-center gap-2 text-sm"
                  >
                    <Save className="w-4 h-4" /> {isSaving ? "Saving..." : "Update Alt-Text"}
                  </button>
                </div>
              )}

              {selectedItem.field_id && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <HelpCircle className="w-4 h-4" /> Form Tooltip (TU)
                  </label>
                  <textarea 
                    value={selectedItem.tooltip || ""}
                    onChange={(e) => setSelectedItem({ ...selectedItem, tooltip: e.target.value })}
                    className="w-full rounded-md border-gray-300 shadow-sm p-2 border h-32"
                    placeholder="Enter accessibility tooltip..."
                  />
                  <button 
                    onClick={() => handleSaveOverride({ tooltip: selectedItem.tooltip })}
                    className="mt-2 w-full bg-purple-700 text-white py-2 rounded flex items-center justify-center gap-2 text-sm"
                  >
                    <Save className="w-4 h-4" /> {isSaving ? "Saving..." : "Update Tooltip"}
                  </button>
                  <div className="mt-4 p-3 bg-purple-50 rounded text-xs text-purple-800">
                    <strong>Internal Name:</strong> {selectedItem.name}
                  </div>
                </div>
              )}

              {selectedItem.text && (
                <div className="pt-6 border-t">
                  <h3 className="text-sm font-semibold mb-2">Original Content</h3>
                  <p className="text-sm text-gray-600 italic">"{selectedItem.text}"</p>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 text-center">
              <ShieldCheck className="w-12 h-12 mb-2 opacity-20" />
              <p>Select a block or form field<br/>to inspect and remediate.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
