// path: frontend/src/components/formforgeapi/components/palette/FieldPalette.jsx
import React from 'react';
import styles from '../../css/FieldPalette.module.css';
import { PALETTE_ITEMS } from '../../constants';
import FieldPaletteItem from './FieldPaletteItem';

const FieldPalette = () => {
  return (
    <aside className={styles.fieldPalette}>
      <h3 className={styles.fieldPalette__title}>Alan Ekle</h3>
      <div className={styles.fieldPalette__list}>
        {PALETTE_ITEMS.map((item) => (
          <FieldPaletteItem
            key={item.type}
            item={item}
          />
        ))}
      </div>
    </aside>
  );
};

export default FieldPalette;