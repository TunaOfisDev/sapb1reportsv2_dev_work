// path: frontend/src/components/formforgeapi/index.js
import FormForgeApiContainer from './containers/FormForgeApiContainer';

/**
 * FormForgeAPI Modül Giriş Noktası
 * --------------------------------------------------------------------
 * Bu dosya, tüm FormForgeAPI özelliğinin ana ihracat noktasıdır.
 *
 * Ana `App.js` dosyasının `import FormForgeApiModule from './components/formforgeapi'`
 * gibi temiz bir import yapabilmesini sağlar.
 *
 * Yaptığı tek şey, modülün tüm iç yönlendirmesini ve yapısını yöneten
 * `FormForgeApiContainer` bileşenini varsayılan olarak ihraç etmektir.
 */
export default FormForgeApiContainer;