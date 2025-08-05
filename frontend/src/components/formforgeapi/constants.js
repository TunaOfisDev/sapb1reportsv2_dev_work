// path: frontend/src/components/formforgeapi/constants.js
/**
 * Genel sabitler
 * ----------------------------------------------------------
 * •  Form alan türleri (Bitrix24-benzeri yeni mimariye uygun)
 * •  Palette/Drag-and-Drop yardımcı sabitleri
 * •  Stil kütüphanesi renk paleti (SAP B1 HANA mavi & sarı)
 * ----------------------------------------------------------
 */

/*-----------------------------------------------------------
| 1) Renk Paleti – tek yerde kalsın, tüm CSS-Modules içe aktarabilir
*----------------------------------------------------------*/
export const COLORS = {
  hanaBlue:  "#0A6ED1",
  hanaBlueDark: "#084C9B",
  hanaYellow: "#F5B800",
  danger: "#C0392B",
  lightGray: "#dfe5e8",
};

/*-----------------------------------------------------------
| 2) Form Alan Tipleri
*----------------------------------------------------------*/
export const FIELD_TYPE_OPTIONS = [
  { value: "text",          label: "Metin" },
  { value: "number",        label: "Sayı" },
  { value: "email",         label: "E-posta" },
  { value: "textarea",      label: "Metin Alanı" },
  { value: "singleselect",  label: "Tekli Seçim" },
  { value: "multiselect",   label: "Çoklu Seçim" },
  { value: "checkbox",      label: "Onay Kutusu" },
  { value: "radio",         label: "Radyo Düğmesi" },
  { value: "date",          label: "Tarih" },
];

/*-----------------------------------------------------------
| 3) Palette Tanımı
|    – FieldPalette.jsx, FieldPaletteItem.jsx kullanır
*----------------------------------------------------------*/
export const DRAG_TYPES = {
  PALETTE_FIELD: "palette-field",
  CANVAS_FIELD:  "canvas-field",
};

export const PALETTE_ITEMS = FIELD_TYPE_OPTIONS.map((opt) => ({
  type: opt.value,
  label: opt.label,
  /* Icon veya kısa etiket eklemek isterseniz burada: */
  /* icon: <SomeSvg /> */
}));

/*-----------------------------------------------------------
| 4) Yeni Alan Şablonu
*----------------------------------------------------------*/
export const createEmptyField = ({
  type = "text",
  order = 0,
  section = 0,
  row = 0,
} = {}) => ({
  id: `temp_${Date.now()}`,
  label: "",
  field_type: type,
  is_required: false,
  is_master: false,
  order,
  section,
  row,
  options:
    type === "singleselect" || type === "multiselect"
      ? []
      : undefined,
});

/*-----------------------------------------------------------
| 5) Grid (section + row) başlangıç şablonu
*----------------------------------------------------------*/
export const createEmptySection = (index = 0) => ({
  id: `section_${index}_${Date.now()}`,
  title: `Section ${index + 1}`,
  rows: [
    { id: `row_${Date.now()}`, fields: [] },
  ],
});
