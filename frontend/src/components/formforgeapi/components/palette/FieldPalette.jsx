// path: frontend/src/components/formforgeapi/components/palette/FieldPalette.jsx
import React from 'react';
import styles from '../../css/FieldPalette.module.css';
import { PALETTE_GROUPS } from '../../constants';
import FieldPaletteItem from './FieldPaletteItem';

const FieldPalette = () => {
  return (
    <aside className={styles.fieldPalette}>
      <h3 className={styles.fieldPalette__title}>Alan Ekle</h3>
      
      {/* DEĞİŞİKLİK: Yapı, grupları render edecek şekilde güncellendi. */}
      <div className={styles.fieldPalette__groupsContainer}>
        {PALETTE_GROUPS.map((group) => (
          <div key={group.id} className={styles.fieldPalette__group}>
            <h4 className={styles.fieldPalette__groupTitle}>{group.label}</h4>
            <div className={styles.fieldPalette__list}>
              {group.items.map((item) => (
                <FieldPaletteItem
                  key={item.type}
                  item={item}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
};

export default FieldPalette;