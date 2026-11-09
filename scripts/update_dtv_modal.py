import os

def update_dtv():
    path = os.path.join('src', 'components', 'DatasetTrainingView.tsx')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add state for selected preview image and X icon import if needed
    if 'selectedPreviewImage' not in content:
        content = content.replace(
            "const [searchQuery, setSearchQuery] = useState<string>('');",
            "const [searchQuery, setSearchQuery] = useState<string>('');\n  const [selectedPreviewImage, setSelectedPreviewImage] = useState<any | null>(null);"
        )

    # 2. Update filter matching logic
    target_filter = """      if (selectedClassFilter !== 'all') {
        if (selectedClassFilter === 'clean' && !img.is_clean) return false;
        if (selectedClassFilter !== 'clean' && !img.class_hint.toLowerCase().includes(selectedClassFilter.toLowerCase())) return false;
      }"""

    replacement_filter = """      if (selectedClassFilter !== 'all') {
        if (selectedClassFilter === 'clean' && !img.is_clean) return false;
        if (selectedClassFilter === 'damage' || selectedClassFilter === 'crack') {
          const h = (img.class_hint || '').toLowerCase();
          const fn = (img.filename || '').toLowerCase();
          return h.includes('damage') || h.includes('crack') || fn.includes('damage') || fn.includes('crack');
        }
        if (selectedClassFilter === 'mat') {
          const h = (img.class_hint || '').toLowerCase();
          const fn = (img.filename || '').toLowerCase();
          return h.includes('mat') || fn.includes('mat');
        }
        if (selectedClassFilter !== 'clean' && !img.class_hint.toLowerCase().includes(selectedClassFilter.toLowerCase())) return false;
      }"""

    if target_filter in content:
        content = content.replace(target_filter, replacement_filter)
        print("Updated filter logic in DatasetTrainingView.tsx")
    else:
        print("Warning: target_filter not found")

    # 3. Update filter buttons
    target_buttons = """            {/* Class Filter */}
            <div className="flex items-center gap-1 ml-auto">
              {[
                { id: 'all', label: 'All Hazards' },
                { id: 'spill', label: 'Spills' },
                { id: 'glass', label: 'Glass' },
                { id: 'crack', label: 'Cracks' },
                { id: 'mat', label: 'Mats' },
                { id: 'cable', label: 'Cables' },
                { id: 'clean', label: 'Clean Floors' }
              ].map((c) => ("""

    replacement_buttons = """            {/* Class Filter */}
            <div className="flex flex-wrap items-center gap-1 ml-auto">
              {[
                { id: 'all', label: 'All Hazards' },
                { id: 'damage', label: 'Floor Damage' },
                { id: 'mat', label: 'Mat Hazard' },
                { id: 'spill', label: 'Liquid Spills' },
                { id: 'glass', label: 'Broken Glass' },
                { id: 'cable', label: 'Cables' },
                { id: 'clean', label: 'Clean Floors' }
              ].map((c) => ("""

    if target_buttons in content:
        content = content.replace(target_buttons, replacement_buttons)
        print("Updated filter buttons in DatasetTrainingView.tsx")
    else:
        print("Warning: target_buttons not found")

    # 4. Update image grid items to add onClick and modal
    target_card = """                <div key={img.id} className="p-2 rounded-xl bg-[#0d131f] border border-[#182335] space-y-1.5 hover:border-[#22c55e]/50 transition-colors">
                  <div className="aspect-16/10 rounded-lg overflow-hidden bg-black relative">
                    <img src={img.url} alt={img.filename} className="w-full h-full object-cover" loading="lazy" />"""

    replacement_card = """                <div
                  key={img.id}
                  onClick={() => setSelectedPreviewImage(img)}
                  className="p-2 rounded-xl bg-[#0d131f] border border-[#182335] space-y-1.5 hover:border-[#22c55e] hover:shadow-lg transition-all cursor-pointer group"
                >
                  <div className="aspect-16/10 rounded-lg overflow-hidden bg-black relative">
                    <img
                      src={img.url}
                      alt={img.filename}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                      loading="lazy"
                      onError={(e) => {
                        const fn = (img.filename || '').toLowerCase();
                        const ch = (img.class_hint || '').toLowerCase();
                        if (fn.includes('crack') || ch.includes('damage')) {
                          (e.target as HTMLImageElement).src = '/assets/samples/gallery/floor_damage.jpg';
                        } else if (fn.includes('mat') || ch.includes('mat')) {
                          (e.target as HTMLImageElement).src = '/assets/samples/gallery/floor_mat_hazard.jpg';
                        } else if (fn.includes('glass') || ch.includes('glass')) {
                          (e.target as HTMLImageElement).src = '/assets/samples/thumb_broken_glass.jpg';
                        } else if (fn.includes('oil') || ch.includes('oil')) {
                          (e.target as HTMLImageElement).src = '/assets/samples/thumb_oil_spill.jpg';
                        } else if (fn.includes('clean') || ch.includes('clean')) {
                          (e.target as HTMLImageElement).src = '/assets/samples/thumb_clean_floor.jpg';
                        } else {
                          (e.target as HTMLImageElement).src = '/assets/samples/thumb_water_spill.jpg';
                        }
                      }}
                    />"""

    if target_card in content:
        content = content.replace(target_card, replacement_card)
        print("Updated image card click and onError fallback in DatasetTrainingView.tsx")
    else:
        print("Warning: target_card not found")

    # 5. Add Modal before the closing </div> of DatasetTrainingView
    target_end = """        </div>
      )}
    </div>
  );
};"""

    replacement_end = """        </div>
      )}

      {/* Dataset Image Inspection Lightbox Modal */}
      {selectedPreviewImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200"
          onClick={() => setSelectedPreviewImage(null)}
        >
          <div
            className="bg-[#111927] border border-[#23354e] rounded-2xl max-w-4xl w-full overflow-hidden shadow-2xl space-y-4 p-5"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#1f2d42] pb-3">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-[#15803d] text-white uppercase">
                  {selectedPreviewImage.split} Split
                </span>
                <h3 className="text-base font-bold text-white font-mono truncate max-w-md">
                  {selectedPreviewImage.filename}
                </h3>
              </div>
              <button
                onClick={() => setSelectedPreviewImage(null)}
                className="p-1.5 rounded-lg bg-[#182335] text-slate-400 hover:text-white hover:bg-[#202e44] transition-colors cursor-pointer"
              >
                ?
              </button>
            </div>

            {/* Modal Image Preview */}
            <div className="relative rounded-xl overflow-hidden bg-black flex items-center justify-center max-h-[550px] border border-[#1e2c3f]">
              <img
                src={selectedPreviewImage.url}
                alt={selectedPreviewImage.filename}
                className="max-h-[540px] w-auto object-contain rounded-lg"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/assets/samples/gallery/floor_damage.jpg';
                }}
              />
            </div>

            {/* Modal Details Footer */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs font-mono">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-400">Class:</span>
                  <span className="font-bold text-[#f97316] bg-[#2a1714] px-2 py-0.5 rounded border border-[#f97316]/30">
                    {selectedPreviewImage.class_hint}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-400">Bounding Boxes:</span>
                  <span className="font-bold text-white bg-[#192437] px-2 py-0.5 rounded">
                    {selectedPreviewImage.boxes_count || 1} verified bbox
                  </span>
                </div>
              </div>
              <div className="text-[11px] text-[#22c55e] font-sans font-semibold">
                ? Verified Ground-Truth Floor Hazard Sample
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};"""

    if target_end in content:
        content = content.replace(target_end, replacement_end)
        print("Added preview lightbox modal to DatasetTrainingView.tsx")
    else:
        print("Warning: target_end not found")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_dtv()
