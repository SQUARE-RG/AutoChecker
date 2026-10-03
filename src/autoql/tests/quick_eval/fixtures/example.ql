import java

class Small extends int {
  Small() { this = [1 .. 3] }
  int doubleValue() { result = this * 2 }
}

predicate pair(int x, int y) {
  x = [1 .. 3] and y = x + 1
}

int successor(int x) {
  x = [1 .. 3] and result = x + 1
}

int functionA(int x) {
  x = [1 .. 3] and result = x + 10
}

int functionB(int x) {
  result = functionA(x) * 2
}

predicate empty(int x) { x = 0 and x = 1 }

from int x, int y
where pair(x, y) and y > 2
select x, y
