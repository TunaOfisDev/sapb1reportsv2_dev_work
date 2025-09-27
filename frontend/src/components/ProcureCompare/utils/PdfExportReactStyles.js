// frontend/src/components/ProcureCompare/utils/PdfExportReactStyles.js

import { StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: {
    padding: 20,
    fontFamily: 'Roboto',
    backgroundColor: 'white',
  },
  header: {
    fontSize: 14,
    marginBottom: 10,
    textAlign: 'center',
    fontWeight: 'bold',
    color: '#333',
  },
  tableContainer: {
    flexDirection: 'column',
    width: '100%',
    marginTop: 5,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#1976d2',
    borderBottomWidth: 0.2,
    borderBottomColor: '#666',
    borderTopWidth: 0.2,
    borderTopColor: '#666',
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 0.2,
    borderBottomColor: '#666',
    minHeight: 20,
  },
  cellHeader: {
    flex: 1,
    padding: 2,
    fontSize: 8,
    color: 'white',
    textAlign: 'center',
    borderLeftWidth: 0.2,
    borderLeftColor: '#666',
    borderRightWidth: 0.2,
    borderRightColor: '#666',
  },
  cell: {
    flex: 1,
    padding: 2,
    fontSize: 7,
    textAlign: 'left',
    borderLeftWidth: 0.2,
    borderLeftColor: '#666',
    borderRightWidth: 0.2,
    borderRightColor: '#666',
  },
  cellLarge: {
    flex: 1.5,
    padding: 2,
    fontSize: 7,
    textAlign: 'left',
    borderLeftWidth: 0.2,
    borderLeftColor: '#666',
    borderRightWidth: 0.2,
    borderRightColor: '#666',
  },
  footer: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    fontSize: 8,
    textAlign: 'left',
    color: '#666',
  },
});

export default styles;
