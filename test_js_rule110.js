const rule = { '111':0, '110':1, '101':1, '100':0, '011':1, '010':1, '001':1, '000':0 };
function step(s) { return s.map((c,i) => rule[`${i>0?s[i-1]:0}${c}${i<s.length-1?s[i+1]:0}`]); }

let state = [0,0,1,0,0];
console.log('Initial:', state);
state = step(state);
console.log('After 1:', state);
state = step(state);
console.log('After 2:', state);





