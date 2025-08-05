// path: frontend/src/components/formforgeapi/components/palette/FieldPaletteItem.jsx
// NOT: Bu dosya @dnd-kit kullanacak şekilde güncellenmiştir.

import React from 'react';
// DEĞİŞTİ: react-beautiful-dnd yerine @dnd-kit/core'dan useDraggable import edildi.
import { useDraggable } from '@dnd-kit/core';
import styles from '../../css/FieldPalette.module.css';

/**
 * FieldPaletteItem Bileşeni (@dnd-kit versiyonu)
 * --------------------------------------------------------------------
 * Bu bileşen, paletten sürüklenen bir kaynak öğedir. 'useDraggable' hook'unu kullanır.
 *
 * @param {Object} item - Görüntülenecek palet öğesi verisi. `{ type, label }`.
 */
const FieldPaletteItem = ({ item }) => {
  // DEĞİŞTİ: <Draggable> sarmalayıcısı yerine useDraggable hook'u kullanıldı.
  const { attributes, listeners, setNodeRef } = useDraggable({
    id: `palette-${item.type}`, // Sürüklenen elemanın benzersiz ID'si
    data: {
      fieldType: item.type,
      isPaletteItem: true, // Bu elemanın paletten geldiğini belirtmek için bir bayrak
    },
  });

  return (
    <div
      ref={setNodeRef} // Sürüklenen DOM düğümünü dnd-kit'e bildirir
      className={styles.fieldPalette__item}
      {...listeners}   // Sürüklemeyi başlatmak için gerekli olay dinleyicileri (örn: onMouseDown)
      {...attributes}  // Erişilebilirlik için gerekli attributelar (örn: role, aria)
    >
      <span className={styles.fieldPalette__label}>{item.label}</span>
    </div>
  );
};

export default FieldPaletteItem;