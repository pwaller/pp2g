# pp2g: print python to go

This is a (currently incomplete and abandoned) experiment to assist in translating python to Go. The goal is not to do a perfect job, but enough that a human can come in and translate it to standalone idiomatic Go.

### You might also like

* [pytogo](https://gitlab.com/esr/pytogo), which takes a similar approach, though it works with lots of regexes rather than parsing the AST.
* [grumpy](https://github.com/google/grumpy) an effort by a Google engineer to translate some code which runs Youtube from Python to Go. As I understand it, it produces runnable code, but it isn't idiomatic or standalone, and implements lots of Python.
* [gython](https://github.com/gython/Gython) which describes itself as "a transpiler written in Python that converts a python like language into Go".

### About

The method it takes is essentially to pretty print the python AST. The only reason it doesn't do this from Go is that there wasn't a python parser written in Go at the time and I wasn't in the mood for writing one :)

To give you a feel of it, this is how it currently translates [`bisect.py`](https://github.com/python/cpython/blob/5f5a7781c8bf7bcc476d3e05d980711be3920724/Lib/bisect.py) from the standard library. You'll note that some constructs aren't yet translated, such as while loops and try blocks. Everything is translated into a comment so that it can be used as a guide.

```go
package bisect

"Bisection algorithms."

// Insert item x in list a, and keep it sorted assuming a is sorted.
// 
//     If x is already in a, insert it to the right of the rightmost x.
// 
//     Optional args lo (default 0) and hi (default len(a)) bound the
//     slice of a to be searched.
func InsortRight(a python.Type, x python.Type, lo python.Type, hi python.Type) {
	// if lo < 0 {
	// 	// unknown Raise('exc', 'cause')
	// }
	// if hi is None {
	// 	hi = len(a)
	// }
	// // unknown While('test', 'body', 'orelse')
	// a.insert(lo, x)
}
var insort = insortRight

// Return the index where to insert item x in list a, assuming a is sorted.
// 
//     The return value i is such that all e in a[:i] have e <= x, and all e in
//     a[i:] have e > x.  So if x already appears in the list, a.insert(x) will
//     insert just after the rightmost x already there.
// 
//     Optional args lo (default 0) and hi (default len(a)) bound the
//     slice of a to be searched.
func BisectRight(a python.Type, x python.Type, lo python.Type, hi python.Type) {
	// if lo < 0 {
	// 	// unknown Raise('exc', 'cause')
	// }
	// if hi is None {
	// 	hi = len(a)
	// }
	// // unknown While('test', 'body', 'orelse')
	// return lo
}
var bisect = bisectRight

// Insert item x in list a, and keep it sorted assuming a is sorted.
// 
//     If x is already in a, insert it to the left of the leftmost x.
// 
//     Optional args lo (default 0) and hi (default len(a)) bound the
//     slice of a to be searched.
func InsortLeft(a python.Type, x python.Type, lo python.Type, hi python.Type) {
	// if lo < 0 {
	// 	// unknown Raise('exc', 'cause')
	// }
	// if hi is None {
	// 	hi = len(a)
	// }
	// // unknown While('test', 'body', 'orelse')
	// a.insert(lo, x)
}

// Return the index where to insert item x in list a, assuming a is sorted.
// 
//     The return value i is such that all e in a[:i] have e < x, and all e in
//     a[i:] have e >= x.  So if x already appears in the list, a.insert(x) will
//     insert just before the leftmost x already there.
// 
//     Optional args lo (default 0) and hi (default len(a)) bound the
//     slice of a to be searched.
func BisectLeft(a python.Type, x python.Type, lo python.Type, hi python.Type) {
	// if lo < 0 {
	// 	// unknown Raise('exc', 'cause')
	// }
	// if hi is None {
	// 	hi = len(a)
	// }
	// // unknown While('test', 'body', 'orelse')
	// return lo
}
// unknown Try('body', 'handlers', 'orelse', 'finalbody')
```
