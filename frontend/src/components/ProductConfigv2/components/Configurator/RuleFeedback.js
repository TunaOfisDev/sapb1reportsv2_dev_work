// frontend/src/components/ProductConfigv2/components/Configurator/RuleFeedback.js

import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/RuleFeedback.css';

/**
 * RuleFeedback bileşeni, ürün konfigüratöründe kural ihlali durumunda
 * kullanıcıya geri bildirim mesajını gösterir.
 *
 * Modern React 2025 standartlarına uygun olarak, erişilebilirlik (role="alert")
 * ve performans optimizasyonu (React.memo) dikkate alınarak oluşturulmuştur.
 *
 * Props:
 * - feedback: Kural ihlaline ilişkin kullanıcıya gösterilecek hata veya uyarı mesajı.
 */
const RuleFeedback = ({ feedback }) => {
  if (!feedback) {
    return null;
  }

  return (
    <div className="rule-feedback" role="alert">
      {feedback}
    </div>
  );
};

RuleFeedback.propTypes = {
  feedback: PropTypes.string,
};

RuleFeedback.defaultProps = {
  feedback: '',
};

export default React.memo(RuleFeedback);
