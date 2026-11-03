#include <iostream>

int find_pair(int limit) {
  int found = -1;
  bool done = false;
  for (int i = 0; i < limit && !done; ++i) {
    for (int j = 0; j < limit; ++j) {
      if (i != j && (i + j) % 7 == 3) {
        found = i * 10 + j;
        done = true;
        break;
      }
    }
  }
  return found;
}

int main() {
  std::cout << find_pair(5) << '\n';
  return 0;
}
