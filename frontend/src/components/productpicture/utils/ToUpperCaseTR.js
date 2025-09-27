// frontend/src/components/productpicture/utils/ToUpperCaseTR.js
// Türkçe karakterler için özel toUpperCase fonksiyonu
const toUpperCaseTR = (str) => {
    const trLowerCase = 'iığüşöç';
    const trUpperCase = 'İIĞÜŞÖÇ';
    const specialCase = {'İ': 'İ'};  // İngilizce 'I' Türkçe'de 'İ' olur.
    let newStr = '';
  
    for (let i = 0; i < str.length; i++) {
      const char = str[i];
      const trIndexLower = trLowerCase.indexOf(char);
      const trIndexUpper = trUpperCase.indexOf(char);
  
      if (trIndexLower !== -1) {
        newStr += trUpperCase[trIndexLower];
      } else if (trIndexUpper !== -1) {
        newStr += trUpperCase[trIndexUpper];
      } else if (specialCase[char]) {
        newStr += specialCase[char];
      } else {
        newStr += char.toUpperCase();
      }
    }
  
    return newStr;
  };
  
  export default toUpperCaseTR;
  