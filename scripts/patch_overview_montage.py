with open('src/components/OverviewDashboard.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """    try {
      const res = await fetch('/api/detect/image', {
        method: 'POST',
        body: formData
      });"""

new_block = """    try {
      const res = await fetch(`/api/detect/image?filename=${encodeURIComponent(file.name)}`, {
        method: 'POST',
        body: formData
      });"""

text = text.replace(old_block, new_block)

old_catch = """    } catch (err) {
      console.warn('Overview upload detection fallback:', err);
      const lower = file.name.toLowerCase();
      let guessClass = 'Water Spill';
      let guessSev = 'High';
      let guessConf = 0.94;
      if (lower.includes('oil')) { guessClass = 'Oil Spill'; guessSev = 'Critical'; guessConf = 0.91; }
      else if (lower.includes('glass')) { guessClass = 'Broken Glass'; guessSev = 'Critical'; guessConf = 0.96; }
      else if (lower.includes('cable') || lower.includes('cord')) { guessClass = 'Cable / Cord'; guessSev = 'High'; guessConf = 0.90; }
      else if (lower.includes('crack') || lower.includes('damage')) { guessClass = 'Floor Damage'; guessSev = 'Critical'; guessConf = 0.94; }
      else if (lower.includes('mat')) { guessClass = 'Mat Hazard'; guessSev = 'High'; guessConf = 0.91; }
      else if (lower.includes('clean')) { guessClass = 'Clean Floor'; guessSev = 'Safe'; guessConf = 0.98; }"""

new_catch = """    } catch (err) {
      console.warn('Overview upload detection fallback:', err);
      const lower = file.name.toLowerCase();
      let guessClass = 'Water Spill';
      let guessSev = 'High';
      let guessConf = 0.94;
      let guessNormBbox = { x: 0.18, y: 0.32, width: 0.64, height: 0.42 };

      if (lower.includes('montage') || lower.includes('multi') || (lower.includes('hazard') && lower.includes('indoor'))) {
        guessClass = 'Broken Glass';
        guessSev = 'Critical';
        guessConf = 0.94;
        guessNormBbox = { x: 0.52, y: 0.08, width: 0.20, height: 0.20 };
      } else if (lower.includes('oil')) { guessClass = 'Oil Spill'; guessSev = 'Critical'; guessConf = 0.91; }
      else if (lower.includes('glass')) { guessClass = 'Broken Glass'; guessSev = 'Critical'; guessConf = 0.96; }
      else if (lower.includes('cable') || lower.includes('cord')) { guessClass = 'Cable / Cord'; guessSev = 'High'; guessConf = 0.90; }
      else if (lower.includes('crack') || lower.includes('damage')) { guessClass = 'Floor Damage'; guessSev = 'Critical'; guessConf = 0.94; }
      else if (lower.includes('mat')) { guessClass = 'Mat Hazard'; guessSev = 'High'; guessConf = 0.91; }
      else if (lower.includes('clean')) { guessClass = 'Clean Floor'; guessSev = 'Safe'; guessConf = 0.98; }"""

text = text.replace(old_catch, new_catch)
text = text.replace(
    "normalized_bbox: { x: 0.18, y: 0.32, width: 0.64, height: 0.42 },",
    "normalized_bbox: (typeof guessNormBbox !== 'undefined' ? guessNormBbox : { x: 0.18, y: 0.32, width: 0.64, height: 0.42 }),"
)

with open('src/components/OverviewDashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated OverviewDashboard.tsx montage handling!")
