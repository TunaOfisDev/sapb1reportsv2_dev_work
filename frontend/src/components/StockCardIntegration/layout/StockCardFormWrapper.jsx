// path: frontend/src/components/StockCardIntegration/layout/StockCardFormWrapper.jsx

import StockCardForm from '../containers/StockCardForm';
import HelptextPanel from '../containers/HelptextPanel';
import styles from '../css/StockCardFormWrapper.module.css';

const StockCardFormWrapper = () => {
  return (
    <div className={styles.layout}>
      <div className={styles.form}>
        <StockCardForm />
      </div>
      <div className={styles.panel}>
        <HelptextPanel />
      </div>
    </div>
  );
};

export default StockCardFormWrapper;
