// node test-search.js
const assert = require('assert');
const { search } = require('./search.js');
const games = require('./games.json');
const top = (q, n = 3) => search(q, games).slice(0, n).map(g => g.t);
const has = (q, title, n = 3) => assert(top(q, n).includes(title), `"${q}" -> ${JSON.stringify(top(q, n))}, wanted ${title}`);

has('moto x3m', 'Moto X3M');
has('motox3m', 'Moto X3M');
has('moto xm3', 'Moto X3M', 1);        // typo
has('frday nite funkin', "Friday Night Funkin'");
has('fnf', "Friday Night Funkin'", 5);  // initials
has('slope', 'Slope 3', 8);
has('fireboy watergirl', 'Fireboy & Watergirl 2 Light Temple', 5);
has('rocket soccer', 'Rocket Soccer Derby');
has('unicycle', 'Unicycle Legend');
has('papas', 'Papa Cheeseria', 10);
assert(search('racing', games).length > 50, 'category words match');
assert.strictEqual(search('zzqqxx', games).length, 0);
console.log('search ok,', games.length, 'games');
