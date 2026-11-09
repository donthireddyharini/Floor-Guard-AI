with open('src/components/DatasetTrainingView.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace hardcoded fallbacks
text = text.replace("|| 160;", "|| 141;") # for totalImgs
text = text.replace("|| 141;", "|| 141;")

# Fix safe navigation in filteredImages
old_filter = """  const filteredImages = useMemo(() => {
    return datasetImages.filter((img) => {
      if (selectedSplitFilter !== 'all' && img.split !== selectedSplitFilter) return false;
      if (selectedClassFilter !== 'all') {
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
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        if (!img.filename.toLowerCase().includes(q) && !img.class_hint.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [datasetImages, selectedSplitFilter, selectedClassFilter, searchQuery]);"""

new_filter = """  const filteredImages = useMemo(() => {
    return datasetImages.filter((img) => {
      if (!img) return false;
      if (selectedSplitFilter !== 'all' && img.split !== selectedSplitFilter) return false;
      const h = (img.class_hint || '').toLowerCase();
      const fn = (img.filename || '').toLowerCase();
      if (selectedClassFilter !== 'all') {
        if (selectedClassFilter === 'clean' && !img.is_clean && !h.includes('clean')) return false;
        if (selectedClassFilter === 'damage' || selectedClassFilter === 'crack') {
          if (!h.includes('damage') && !h.includes('crack') && !fn.includes('damage') && !fn.includes('crack')) return false;
        } else if (selectedClassFilter === 'mat') {
          if (!h.includes('mat') && !fn.includes('mat')) return false;
        } else if (selectedClassFilter === 'spill') {
          if (!h.includes('spill') && !fn.includes('spill') && !h.includes('water') && !h.includes('oil') && !h.includes('chemical')) return false;
        } else if (selectedClassFilter === 'glass') {
          if (!h.includes('glass') && !fn.includes('glass')) return false;
        } else if (selectedClassFilter === 'cable') {
          if (!h.includes('cable') && !h.includes('cord') && !fn.includes('cable') && !fn.includes('cord')) return false;
        } else if (selectedClassFilter !== 'clean') {
          if (!h.includes(selectedClassFilter.toLowerCase())) return false;
        }
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        if (!fn.includes(q) && !h.includes(q)) return false;
      }
      return true;
    });
  }, [datasetImages, selectedSplitFilter, selectedClassFilter, searchQuery]);"""

text = text.replace(old_filter, new_filter)

# Add onError on image cards in gallery
old_card_img = """                      <img
                        src={img.url || '/assets/samples/thumb_water_spill.jpg'}
                        alt={img.filename}
                        className="w-full h-full object-cover transition-transform group-hover:scale-105"
                      />"""

new_card_img = """                      <img
                        src={img.url || '/assets/samples/thumb_water_spill.jpg'}
                        alt={img.filename}
                        onError={(e) => {
                          (e.currentTarget as HTMLImageElement).onerror = null;
                          (e.currentTarget as HTMLImageElement).src = '/assets/samples/thumb_water_spill.jpg';
                        }}
                        className="w-full h-full object-cover transition-transform group-hover:scale-105"
                      />"""

text = text.replace(old_card_img, new_card_img)

with open('src/components/DatasetTrainingView.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated DatasetTrainingView.tsx successfully!")
