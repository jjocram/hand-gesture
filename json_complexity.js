const {isNull} = require('util');

fs = require('fs')

let isType = (val, Cls) => val != null && val.constructor === Cls;
let getComplexity = (json, d=1.05) => {
  
  // Here `d` is our "depth factor"
  
  return d * (() => {

    // String
    if (isType(json, String)) return 1;

    // Number
    if (isType(json, Number)) return 1;

    // Null values 
    if (isNull(json)) return 1;

    // Arrays are 1 + (average complexity of nested elements)
    if (isType(json, Array)) {
      let avg = json.reduce((o, v) => o + getComplexity(v, d), 0) / (json.length || 1);
      return avg + 1;
    }

    // Objects are 1 + (average complexity of their keys) + (average complexity of their values)
    if (isType(json, Object)) {
      // `getComplexity` for Arrays will add 1 twice, so subtract 1 to compensate
      //return getComplexity(Object.keys(json), d) + getComplexity(Object.values(json), d) - 1;
      return getComplexity(Object.values(json));
    }

    throw new Error(`Couldn't get complexity of ${json}`);
    
  })();
  
};

fs.readFile(process.argv[2], 'utf8', function(err, data) {
  if (err) {
      return console.log(err);
  }

  jsonFile = JSON.parse(data);
  console.log(getComplexity(jsonFile));
});
